import threading
from typing import Any, Literal, Optional, Protocol

from union._datastructures import ActionID
from union._task import TaskTemplate

__all__ = ["Controller", "ControllerType", "create_controller", "get_controller"]

ControllerType = Literal["local", "remote"]


class Controller(Protocol):
    """
    Controller interface, that is used to execute tasks. The implementation of this interface,
    can execute tasks in different ways, such as locally, remotely etc.
    """

    async def submit(self, _task: TaskTemplate, *args, **kwargs) -> Any:
        """
        Submit a node to the controller asynchronously and wait for the result. This is async and will block
        the current coroutine until the result is available.
        """
        ...

    async def finalize_parent_action(self, action: ActionID):
        """
        Finalize the parent action. This can be called to cleanup the action and should be called after the parent
        task completes
        :param action: Action ID
        :return:
        """
        ...

    def stop(self):
        """
        Stops the engine and should be called when the engine is no longer needed.
        """
        ...


# Internal state holder
class _ControllerState:
    controller: Optional[Controller] = None
    lock = threading.Lock()


async def get_controller() -> Controller:
    """
    Get the controller instance. Raise an error if it has not been created.
    """
    if _ControllerState.controller is not None:
        return _ControllerState.controller
    raise RuntimeError("Controller is not initialized. Please call get_or_create_controller() first.")


def create_controller(
    ct: ControllerType,
    **kwargs,
) -> Controller:
    """
    Create a new instance of the controller, based on the kind and the given configuration.
    """
    match ct:
        case "local":
            from ._local_controller import LocalController

            controller = LocalController()
        case ("remote" | "hybrid"):
            from union._internal.controllers.remote import create_remote_controller

            controller = create_remote_controller(**kwargs)
        case _:
            raise ValueError(f"{ct} is not a valid controller type.")

    with _ControllerState.lock:
        _ControllerState.controller = controller
        return controller
