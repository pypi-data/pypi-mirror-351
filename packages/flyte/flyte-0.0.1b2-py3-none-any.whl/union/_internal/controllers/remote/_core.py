from __future__ import annotations

import asyncio
import sys
import threading
from asyncio import Event
from typing import Awaitable, Coroutine, Dict, Optional

import grpc.aio

import union.errors
from union._logging import log, logger
from union._protos.workflow import queue_service_pb2, run_definition_pb2, task_definition_pb2
from union.errors import RuntimeSystemError

from ._action import Action
from ._informer import Informer, InformerCache
from ._service_protocol import ClientSet, QueueService, StateService


class Controller:
    """
    Generic controller with high-level submit API running in a dedicated thread with its own event loop.
    All methods that begin with _bg_ are run in the controller's event loop, and will need to use
    _run_coroutine_in_controller_thread to run them in the controller's event loop.
    """

    def __init__(
        self,
        client_coro: Awaitable[ClientSet],
        workers: int = 2,
        max_system_retries: int = 5,
        resource_log_interval_sec: float = 10.0,
        min_backoff_on_err_sec: float = 0.1,
        thread_wait_timeout_sec: float = 10.0,
    ):
        """
        Create a new controller instance.
        :param workers: Number of worker threads.
        :param max_system_retries: Maximum number of system retries.
        :param resource_log_interval_sec: Interval for logging resource stats.
        :param min_backoff_on_err_sec: Minimum backoff time on error.
        :param thread_wait_timeout_sec: Timeout for waiting for the controller thread to start.
        :param
        """
        self._informers = InformerCache()
        self._shared_queue = asyncio.Queue(maxsize=10000)
        self._running = False
        self._completion_events: Dict[str, Event] = {}  # Track completion events
        self._resource_log_task = None
        self._workers = workers
        self._max_retries = max_system_retries
        self._resource_log_interval = resource_log_interval_sec
        self._min_backoff_on_err = min_backoff_on_err_sec
        self._thread_wait_timeout = thread_wait_timeout_sec
        self._client_coro = client_coro

        self._initialize_lock: Dict[str, asyncio.Lock] = {}

        # Thread management
        self._thread = None
        self._loop = None
        self._thread_ready = threading.Event()
        self._thread_exception = None
        self._thread_com_lock = threading.Lock()
        self._start()

    # ---------------- Public sync methods, we can add more sync methods if needed
    @log
    def submit_action_sync(self, action: Action) -> Action:
        """Synchronous version of submit that runs in the controller's event loop"""
        fut = self._run_coroutine_in_controller_thread(self._bg_submit_action(action))
        return fut.result()

    # --------------- Public async methods
    async def _initialize_parent_action(
        self, run_id: run_definition_pb2.RunIdentifier, parent_action_name: str, timeout: Optional[float] = None
    ):
        name = Informer.mkname(run_name=run_id.name, parent_action_name=parent_action_name)
        if name not in self._initialize_lock:
            self._initialize_lock[name] = asyncio.Lock()
        # We want to limit the coroutines working on this parent run from entering the initialization section,
        # as we just want one informer to be initialized. This is why we take the lock. After the first one,
        # subsequent initializations should be fast!!!!!
        async with self._initialize_lock[name]:
            return await self._run_coroutine_in_controller_thread(
                self._bg_create_new_informer_and_wait(run_id, parent_action_name, timeout=timeout)
            )

    @log
    async def submit_action(self, action: Action) -> Action:
        """Public API to submit a resource and wait for completion"""
        await self._initialize_parent_action(
            run_id=action.action_id.run, parent_action_name=action.parent_action_name, timeout=self._thread_wait_timeout
        )
        return await self._run_coroutine_in_controller_thread(self._bg_submit_action(action))

    async def _finalize_parent_action(
        self, run_id: run_definition_pb2.RunIdentifier, parent_action_name: str, timeout: Optional[float] = None
    ):
        """Finalize the parent run"""
        name = Informer.mkname(run_name=run_id.name, parent_action_name=parent_action_name)
        lock = self._initialize_lock.get(name)
        if lock is None:
            return
        async with lock:
            await self._run_coroutine_in_controller_thread(
                self._bg_finalize_informer(run_id=run_id, parent_action_name=parent_action_name, timeout=timeout)
            )
        self._initialize_lock.pop(name, None)

    @log
    def stop(self, timeout: Optional[float] = None):
        """Stop the controller"""
        return asyncio.wait_for(self._run_coroutine_in_controller_thread(self._bg_stop()), timeout)

    # ------------- Background thread management methods
    def _set_exception(self, exc: Optional[BaseException]):
        """Set exception in the thread lock"""
        with self._thread_com_lock:
            self._thread_exception = exc

    def _get_exception(self) -> Optional[BaseException]:
        """Get exception in the thread lock"""
        with self._thread_com_lock:
            return self._thread_exception

    @log
    def _start(self):
        """Start the controller in a separate thread"""
        if self._thread and self._thread.is_alive():
            logger.warning("Controller thread is already running")
            return

        self._thread_ready.clear()
        self._set_exception(None)
        self._thread = threading.Thread(target=self._bg_thread_target, daemon=True, name="ControllerThread")
        self._thread.start()

        # Wait for the thread to be ready
        logger.info("Waiting for controller thread to be ready...")
        if not self._thread_ready.wait(timeout=self._thread_wait_timeout):
            raise TimeoutError("Controller thread failed to start in time")

        if self._get_exception():
            raise RuntimeSystemError(
                type(self._get_exception()).__name__, f"Controller thread startup failed: {self._get_exception()}"
            )

        logger.info(f"Controller started in thread: {self._thread.name}")

    def _run_coroutine_in_controller_thread(self, coro: Coroutine) -> asyncio.Future:
        """Run a coroutine in the controller's event loop and return the result"""
        with self._thread_com_lock:
            loop = self._loop
            if not self._loop or not self._thread or not self._thread.is_alive():
                raise RuntimeError("Controller thread is not running")

        assert self._thread.name != threading.current_thread().name, "Cannot run coroutine in the same thread"

        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return asyncio.wrap_future(future)

    # ------------- Private methods that run on the background thread
    async def _bg_worker_pool(self):
        logger.debug("Starting controller worker pool")
        self._running = True
        logger.debug("Waiting for Service Client to be ready")
        client_set = await self._client_coro
        self._state_service: StateService = client_set.state_service
        self._queue_service: QueueService = client_set.queue_service
        self._resource_log_task = asyncio.create_task(self._bg_log_stats())
        # We will wait for this to signal that the thread is ready
        # Signal the main thread that we're ready
        logger.debug("Background thread initialization complete")
        self._thread_ready.set()
        if sys.version_info >= (3, 11):
            async with asyncio.TaskGroup() as tg:
                for i in range(self._workers):
                    tg.create_task(self._bg_run())
        else:
            tasks = []
            for i in range(self._workers):
                tasks.append(asyncio.create_task(self._bg_run()))
            await asyncio.gather(*tasks)

    def _bg_thread_target(self):
        """Target function for the controller thread that creates and manages its own event loop"""
        try:
            # Create a new event loop for this thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            logger.debug(f"Controller thread started with new event loop: {threading.current_thread().name}")

            self._loop.run_until_complete(self._bg_worker_pool())
        except Exception as e:
            logger.error(f"Controller thread encountered an exception: {e}")
            self._set_exception(e)
        finally:
            if self._loop and self._loop.is_running():
                self._loop.close()
            logger.debug(f"Controller thread exiting: {threading.current_thread().name}")

    async def _bg_create_new_informer_and_wait(
        self, run_id: run_definition_pb2.RunIdentifier, parent_action_name: str, timeout: Optional[float] = None
    ):
        if await self._informers.has(run_name=run_id.name, parent_action_name=parent_action_name):
            return
        informer = Informer(
            run_id=run_id,
            parent_action_name=parent_action_name,
            shared_queue=self._shared_queue,
            client=self._state_service,
        )
        await informer.start(timeout=timeout)
        await self._informers.add(informer)

    async def _bg_finalize_informer(
        self, run_id: run_definition_pb2.RunIdentifier, parent_action_name: str, timeout: Optional[float] = None
    ):
        informer = await self._informers.remove(run_name=run_id.name, parent_action_name=parent_action_name)
        if informer:
            await informer.stop()

    @log
    async def _bg_submit_action(self, action: Action) -> Action:
        """Submit a resource and await its completion, returning the final state"""
        logger.debug(f"{threading.current_thread().name} Submitting action {action.name}")
        informer = await self._informers.get(run_name=action.run_name, parent_action_name=action.parent_action_name)
        # Create completion event and add resource
        self._completion_events[action.name] = Event()
        await informer.submit(action)

        logger.debug(f"{threading.current_thread().name} Waiting for completion of {action.name}")
        # Wait for completion
        await self._completion_events[action.name].wait()
        logger.info(f"{threading.current_thread().name} Action {action.name} completed")

        # Get final resource state and clean up
        final_resource = await informer.get(action.name)
        if final_resource is None:
            raise ValueError(f"Action {action.name} not found")
        del self._completion_events[action.name]
        logger.debug(f"{threading.current_thread().name} Removed completion event for action {action.name}")
        await informer.remove(action.name)  # TODO we should not remove maybe, we should keep a record of completed?
        logger.debug(f"{threading.current_thread().name} Removed action {action.name}, final={final_resource}")
        return final_resource

    async def _bg_launch(self, action: Action):
        """
        Attempt to launch an action.
        """
        if not action.is_started():
            logger.debug(f"Attempting to launch action: {action.name}")
            try:
                await self._queue_service.EnqueueAction(
                    queue_service_pb2.EnqueueActionRequest(
                        action_id=action.action_id,
                        parent_action_name=action.parent_action_name,
                        task_id=task_definition_pb2.TaskIdentifier(
                            version=action.task.task_template.id.version,
                            org=action.task.task_template.id.org,
                            project=action.task.task_template.id.project,
                            domain=action.task.task_template.id.domain,
                            name=action.task.task_template.id.name,
                        ),
                        task_spec=action.task,
                        input_uri=action.inputs_uri,
                        output_uri=action.outputs_uri,
                        group=action.group,
                        # Subject is not used in the current implementation
                    )
                )
                logger.info(f"Successfully launched action: {action.name}")
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                    logger.info(f"Action {action.name} already exists, continuing to monitor.")
                    return
                logger.exception(f"Failed to launch action: {action.name} backing off...")
                logger.debug(f"Action details: {action}")
                raise e

    @log
    async def _bg_process(self, action: Action):
        """Process resource updates"""
        logger.debug(f"Processing action: name={action.name}, started={action.is_started()}")

        if not action.is_started():
            await self._bg_launch(action)
        elif action.is_terminal():
            if action.name in self._completion_events:
                # TODO This can conflict, we probably need a completion cache.
                self._completion_events[action.name].set()  # Signal completion
        else:
            logger.debug(f"Resource {action.name} still in progress...")

    async def _bg_log_stats(self):
        """Periodically log resource stats if debug is enabled"""
        while self._running:
            async for started, pending, terminal in self._informers.count_started_pending_terminal_actions():
                logger.info(f"Resource stats: Started={started}, Pending={pending}, Terminal={terminal}")
            await asyncio.sleep(self._resource_log_interval)

    @log
    async def _bg_run(self):
        """Run loop with resource status logging"""
        while self._running:
            logger.debug(f"{threading.current_thread().name} Waiting for resource")
            action = await self._shared_queue.get()
            logger.debug(f"{threading.current_thread().name} Got resource {action.name}")
            try:
                await self._bg_process(action)
            except Exception as e:
                logger.error(f"Error in controller loop: {e}")
                # TODO we need a better way of handling backoffs currently the entire worker coroutine backs off
                await asyncio.sleep(self._min_backoff_on_err)
                action.increment_retries()
                if action.retries > self._max_retries:
                    err = union.errors.RuntimeSystemError(
                        code=type(e).__name__,
                        message=f"Controller failed, system retries {action.retries}"
                        f" crossed threshold {self._max_retries}",
                    )
                    err.__cause__ = e
                    action.set_client_error(err)
                    if action.name in self._completion_events:
                        self._completion_events[action.name].set()  # Signal completion
                else:
                    await self._shared_queue.put(action)
            finally:
                self._shared_queue.task_done()

    @log
    async def _bg_stop(self):
        """Stop the controller"""
        self._running = False
        for event in self._completion_events.values():
            event.set()  # Unblock any waiting submit calls
        self._completion_events.clear()
        self._resource_log_task.cancel()
        await self._informers.remove_and_stop_all()
