import importlib
from typing import List

from union._internal.resolvers._task_module import extract_task_module
from union._internal.resolvers.common import Resolver
from union._task import TaskTemplate


class DefaultTaskResolver(Resolver):
    """
    Please see the notes in the TaskResolverMixin as it describes this default behavior.
    """

    @property
    def import_path(self) -> str:
        return "union._internal.resolvers.default.DefaultTaskResolver"

    def load_task(self, loader_args: List[str]) -> TaskTemplate:
        _, task_module, _, task_name, *_ = loader_args

        task_module = importlib.import_module(name=task_module)  # type: ignore
        task_def = getattr(task_module, task_name)
        return task_def

    def loader_args(self, task: TaskTemplate) -> List[str]:  # type:ignore
        t, m = extract_task_module(task)
        return ["mod", m, "instance", t]
