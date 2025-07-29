from asyncio import Protocol
from typing import List

from union._task import TaskTemplate


class Resolver(Protocol):
    """
    Resolver interface for loading tasks. This interface should be implemented by Resolvers.
    """

    @property
    def import_path(self) -> str: ...

    def load_task(self, loader_args: List[str]) -> TaskTemplate:
        """
        Given the set of identifier keys, should return one TaskTemplate or raise an error if not found
        """

    def loader_args(self, t: TaskTemplate) -> List[str]:
        """
        Return a list of strings that can help identify the parameter TaskTemplate. Each string should not have
        spaces or special characters. This is used to identify the task in the resolver.
        """
