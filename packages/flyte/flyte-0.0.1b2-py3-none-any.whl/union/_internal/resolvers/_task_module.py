import inspect
import pathlib
import sys
from typing import Tuple

from union._task import AsyncFunctionTaskTemplate, TaskTemplate


def extract_task_module(task: TaskTemplate) -> Tuple[str, str]:
    """
    Extract the task module from the task template.

    :param task: The task template to extract the module from.
    :return: A tuple containing the entity name, module
    """
    # TODO Work with current working directory, to figure out the module name, in case of nested launches
    entity_name = task.name
    if isinstance(task, AsyncFunctionTaskTemplate):
        entity_module = inspect.getmodule(task.func).__name__
        entity_name = task.func.__name__
    else:
        raise NotImplementedError(f"Task module {entity_name} not implemented.")

    if entity_module == "__main__":
        """
        This case is for the case in which the task is run from the main module.
        """
        main_path = pathlib.Path(sys.modules["__main__"].__file__)
        entity_module = main_path.stem

    return entity_name, entity_module
