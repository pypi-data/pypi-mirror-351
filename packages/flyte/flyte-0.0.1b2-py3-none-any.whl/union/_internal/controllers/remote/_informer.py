from __future__ import annotations

import asyncio
from asyncio import Queue
from typing import AsyncIterator, Dict, Optional, Tuple

import grpc.aio

from union._logging import log, logger
from union._protos.workflow import run_definition_pb2, state_service_pb2

from ._action import Action
from ._service_protocol import StateService


class ActionCache:
    """
    Cache for actions, used to store the state of all sub-actions, launched by this parent action.
    This is coroutine-safe.
    """

    def __init__(self, parent_action_name: str):
        self._cache: Dict[str, Action] = {}
        self._lock = asyncio.Lock()
        self._parent_action_name = parent_action_name

    async def has(self, name: str) -> bool:
        """Check if a node is in the cache"""
        async with self._lock:
            return name in self._cache

    async def observe_state(self, state: state_service_pb2.ActionUpdate) -> Action:
        """
        Add an action to the cache if it doesn't exist. This is invoked by the watch.
        """
        logger.debug(f"Observing phase {run_definition_pb2.Phase.Name(state.phase)} for {state.action_id.name}")
        if state.phase == run_definition_pb2.Phase.PHASE_FAILED:
            logger.error(
                f"Action {state.action_id.name} failed with error (msg):"
                f" [{state.error if state.HasField('error') else None}]"
            )
        async with self._lock:
            if state.action_id.name in self._cache:
                self._cache[state.action_id.name].merge_state(state)
            else:
                self._cache[state.action_id.name] = Action.from_state(self._parent_action_name, state)
            return self._cache[state.action_id.name]

    async def submit(self, action: Action) -> Action:
        """
        Submit a new Action to the cache. This is invoked by the parent_action.
        """
        async with self._lock:
            if action.name in self._cache:
                self._cache[action.name].merge_in_action_from_submit(action)
            else:
                self._cache[action.name] = action
            return self._cache[action.name]

    async def get(self, name: str) -> Action | None:
        """Get an action by its name from the cache"""
        async with self._lock:
            return self._cache.get(name, None)

    async def remove(self, name: str) -> Action | None:
        """Remove an action from the cache"""
        async with self._lock:
            return self._cache.pop(name, None)

    async def count_started_pending_terminal_actions(self) -> Tuple[int, int, int]:
        """
        Get all started, pending and terminal actions.
        Started: implies they were submitted to queue service
        Pending: implies they are still not submitted to the queue service
        Terminal: implies completed (success, failure, aborted, timedout) actions
        """
        started = 0
        pending = 0
        terminal = 0
        async with self._lock:
            for name, res in self._cache.items():
                if res.is_started():
                    started += 1
                elif res.is_terminal():
                    terminal += 1
                else:
                    pending += 1
            return started, pending, terminal


class Informer:
    """Remote StateStore watcher and informer for sub-actions."""

    def __init__(
        self,
        run_id: run_definition_pb2.RunIdentifier,
        parent_action_name: str,
        shared_queue: Queue,
        client: StateService = None,
        watch_backoff_interval_sec: float = 1.0,
    ):
        self.name = self.mkname(run_name=run_id.name, parent_action_name=parent_action_name)
        self.parent_action_name = parent_action_name
        self._run_id = run_id
        self._client = client
        self._action_cache = ActionCache(parent_action_name)
        self._shared_queue = shared_queue
        self._running = False
        self._watch_task: asyncio.Task | None = None
        self._ready = asyncio.Event()
        self._watch_backoff_interval_sec = watch_backoff_interval_sec

    @classmethod
    def mkname(cls, *, run_name: str, parent_action_name: str) -> str:
        """Get the name of the informer"""
        return f"{run_name}.{parent_action_name}"

    def is_running(self) -> bool:
        """Check if informer is running"""
        return self._running

    async def _set_ready(self):
        """Set the informer as ready"""
        self._ready.set()

    async def wait_for_cache_sync(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the informer to be ready. In the case of a timeout, it will return False.
        :param timeout: float time to wait for
        :return: bool
        """
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Informer cache sync timed out, for {self.name}")
            return False

    @log
    async def submit(self, action: Action):
        """Add a new resource to watch"""
        node = await self._action_cache.submit(action)
        await self._shared_queue.put(node)

    @log
    async def remove(self, name: str):
        """Remove a resource from watching"""
        await self._action_cache.remove(name)

    async def get(self, name: str) -> Action | None:
        """Get a resource by name"""
        return await self._action_cache.get(name)

    async def has(self, name: str) -> bool:
        """Check if a resource exists"""
        return await self._action_cache.has(name)

    async def watch(self):
        """Watch for updates on all resources - to be implemented by subclasses for watch mode"""
        # sentinel = False
        while self._running:
            try:
                watcher = self._client.Watch(
                    state_service_pb2.WatchRequest(
                        parent_action_id=run_definition_pb2.ActionIdentifier(
                            name=self.parent_action_name,
                            run=self._run_id,
                        ),
                    ),
                )
                resp: state_service_pb2.WatchResponse
                async for resp in watcher:
                    if resp.control_message is not None and resp.control_message.sentinel:
                        logger.info(f"Received Sentinel, for run {self.name}")
                        await self._set_ready()
                        continue
                    node = await self._action_cache.observe_state(resp.action_update)
                    await self._shared_queue.put(node)
                    # hack to work in the absence of sentinel
            except asyncio.CancelledError as e:
                logger.warning(f"Watch cancelled: {self.name} {e!s}")
            except asyncio.TimeoutError:
                logger.exception(f"Watch timeout: {self.name}")
            except grpc.aio.AioRpcError:
                logger.exception(f"RPC error: {self.name}")
            except Exception:
                logger.exception(f"Watch error: {self.name}")
            await asyncio.sleep(self._watch_backoff_interval_sec)

    @log
    async def start(self, timeout: Optional[float] = None):
        """Start the informer"""
        if self._running:
            logger.warning("Informer already running")
            return
        self._running = True
        self._watch_task = asyncio.create_task(self.watch())
        await self.wait_for_cache_sync(timeout=timeout)

    async def count_started_pending_terminal_actions(self) -> Tuple[int, int, int]:
        """Get all launched and waiting resources"""
        return await self._action_cache.count_started_pending_terminal_actions()

    @log
    async def stop(self):
        """Stop the informer"""
        self._running = False
        if self._watch_task:
            self._watch_task.cancel()
            self._watch_task = None
        logger.info("Stopped informer")


class InformerCache:
    """Cache for informers, used to store the state of all subactions for multiple parent_actions.
    This is coroutine-safe.
    """

    def __init__(self):
        self._cache: Dict[str, Informer] = {}
        self._lock = asyncio.Lock()

    @log
    async def add(self, informer: Informer) -> bool:
        """Add a new informer to the cache"""
        async with self._lock:
            if informer.name in self._cache:
                return False
            self._cache[informer.name] = informer
            return True

    @log
    async def get(self, *, run_name: str, parent_action_name: str) -> Informer | None:
        """Get an informer by name"""
        async with self._lock:
            return self._cache.get(Informer.mkname(run_name=run_name, parent_action_name=parent_action_name), None)

    @log
    async def remove(self, *, run_name: str, parent_action_name: str) -> Informer | None:
        """Remove an informer from the cache"""
        async with self._lock:
            return self._cache.pop(Informer.mkname(run_name=run_name, parent_action_name=parent_action_name), None)

    async def has(self, *, run_name: str, parent_action_name: str) -> bool:
        """Check if an informer exists in the cache"""
        async with self._lock:
            return Informer.mkname(run_name=run_name, parent_action_name=parent_action_name) in self._cache

    async def count_started_pending_terminal_actions(self) -> AsyncIterator[Tuple[int, int, int]]:
        """Log resource stats"""
        async with self._lock:
            for informer in self._cache.values():
                yield await informer.count_started_pending_terminal_actions()

    async def remove_and_stop_all(self):
        """Stop all informers and remove them from the cache"""
        async with self._lock:
            while self._cache:
                name, informer = self._cache.popitem()
                await informer.stop()
            self._cache.clear()
