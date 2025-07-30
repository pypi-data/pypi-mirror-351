from __future__ import annotations

from threading import Lock
from typing import Any, Callable, Coroutine, Dict, Literal, Optional, Union

import rich.repr
from flyteidl.core import interface_pb2

from union import CacheRequest, Resources, ReusePolicy
from union._api_commons import syncer
from union._initialize import get_client, get_common_config, requires_client
from union._protos.workflow import task_definition_pb2, task_service_pb2
from union._retry import RetryStrategy
from union._secret import SecretRequest
from union._timeout import TimeoutType


class LazyEntity:
    """
    Fetches the entity when the entity is called or when the entity is retrieved.
    The entity is derived from RemoteEntity so that it behaves exactly like the mimicked entity.
    """

    def __init__(self, name: str, getter: Callable[[], Coroutine[Any, Any, Task]], *args, **kwargs):
        self._task = None
        self._getter = getter
        self._name = name
        if not self._getter:
            raise ValueError("getter method is required to create a Lazy loadable Remote Entity.")
        self._mutex = Lock()

    @property
    def name(self) -> str:
        return self._name

    @requires_client
    @syncer.wrap
    async def fetch(self) -> Task:
        """
        Forwards all other attributes to task, causing the task to be fetched!
        """
        with self._mutex:
            if self._task is None:
                try:
                    self._task = await self._getter()
                except AttributeError as e:
                    raise RuntimeError(
                        f"Error downloading the entity {self._name}, (check original exception...)"
                    ) from e
            return self._task

    @requires_client
    async def __call__(self, *args, **kwargs):
        """
        Forwards the call to the underlying task. The entity will be fetched if not already present
        """
        tk = await self.fetch.aio()
        return await tk(*args, **kwargs)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"Future for task with name {self._name}"


def _interface_repr(name: str, interface: interface_pb2.TypedInterface) -> str:
    """
    Returns a string representation of the task interface.
    """
    i = f"{name}("
    if interface.inputs:
        initial = True
        for key, tpe in interface.inputs.variables.items():
            if not initial:
                i += ", "
            i += f"{key}"
    i += ")"
    if interface.outputs:
        initial = True
        multi = len(interface.outputs.variables) > 1
        i += " -> "
        if multi:
            i += "("
        for key, tpe in interface.outputs.variables.items():
            if not initial:
                i += ", "
            i += f"{key}"
        if multi:
            i += ")"
    i += ":"
    return i


class Task:
    @classmethod
    def _parse_task_url(cls, task_url) -> task_definition_pb2.TaskIdentifier:
        if not task_url.startswith("task://"):
            raise ValueError("Invalid task URL: must start with 'task://'")

        parts = task_url[len("task://") :].split("/")

        if len(parts) != 5:
            raise ValueError("Invalid task URL: must have 5 parts after 'task://'")

        org, project, domain, name, version = parts
        return task_definition_pb2.TaskIdentifier(
            org=org,
            project=project,
            domain=domain,
            name=name,
            version=version,
        )

    @classmethod
    def get(cls, uri: str | None = None, *, name: str | None = None, version: str | None = None) -> LazyEntity:
        """
        Get a task by its ID or name. If both are provided, the ID will take precedence.

        :param uri: The URI of the task. If provided, do not provide the rest of the parameters.
        :param name: The name of the task.
        :param version: The version of the task.

        """
        if uri:
            task_id = cls._parse_task_url(uri)
        else:
            cfg = get_common_config()
            task_id = task_definition_pb2.TaskIdentifier(
                org=cfg.org,
                project=cfg.project,
                domain=cfg.domain,
                name=name,
                version=version,
            )

        @requires_client
        async def deferred_get() -> Task:
            resp = await get_client().task_service.GetTaskDetails(
                task_service_pb2.GetTaskDetailsRequest(
                    task_id=task_id,
                )
            )
            return cls(resp.details)

        return LazyEntity(name=name, getter=deferred_get)

    def __init__(self, task: task_definition_pb2.TaskDetails):
        self._task = task

    @requires_client
    def __call__(self, *args, **kwargs):
        """
        Forwards the call to the underlying task. The entity will be fetched if not already present
        """
        raise NotImplementedError

    def __getattr__(self, item: str) -> Any:
        """
        Forwards all other attributes to task, causing the task to be fetched!
        """
        return getattr(self._task, item)

    def override(
        self,
        *,
        local: Optional[bool] = None,
        ref: Optional[bool] = None,
        resources: Optional[Resources] = None,
        cache: CacheRequest = "auto",
        retries: Union[int, RetryStrategy] = 0,
        timeout: Optional[TimeoutType] = None,
        reusable: Union[ReusePolicy, Literal["auto"], None] = None,
        env: Optional[Dict[str, str]] = None,
        secrets: Optional[SecretRequest] = None,
        **kwargs: Any,
    ) -> Task:
        raise NotImplementedError

    def __rich_repr__(self) -> rich.repr.Result:
        """
        Rich representation of the task.
        """
        yield "project", self._task.task_id.project
        yield "domain", self._task.task_id.domain
        yield "name", self._task.task_id.name
        yield "version", self._task.task_id.version
        yield "deployed by", self._task.metadata.deployed_by
        yield "interface", _interface_repr(self._task.task_id.name, self._task.spec.task_template.interface)


if __name__ == "__main__":
    tk = Task.get(name="example_task")
