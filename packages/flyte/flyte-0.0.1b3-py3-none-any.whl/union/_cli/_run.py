from __future__ import annotations

from union._logging import logger
from dataclasses import dataclass, fields
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, cast

import click

import union

from .._code_bundle._utils import CopyFiles
from .._initialize import initialize_in_cluster, S3
from .._task import TaskTemplate
from . import _common as common
from ._common import CLIConfig


@dataclass
class RunArguments:
    project: str = common.make_click_option_field(common.PROJECT_OPTION)
    domain: str = common.make_click_option_field(common.DOMAIN_OPTION)
    local: bool = common.make_click_option_field(
        click.Option(
            ["--local"],
            is_flag=True,
            help="Run the task locally",
        )
    )
    hybrid: bool = common.make_click_option_field(
        click.Option(
            ["--hybrid"],
            is_flag=True,
            help="hybrid mode",
        )
    )
    copy_style: CopyFiles = common.make_click_option_field(
        click.Option(
            ["--copy-style"],
            type=click.Choice(["loaded_modules", "all_files", "none"]),
            default="loaded_modules",
            help="Copy style to use when running the task",
        )
    )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RunArguments:
        return cls(**d)

    @classmethod
    def options(cls) -> List[click.Option]:
        """
        Return the set of base parameters added to run subcommand.
        """
        return [common.get_option_from_metadata(f.metadata) for f in fields(cls) if f.metadata]


class RunTaskCommand(click.Command):
    def __init__(self, obj_name: str, obj: Any, run_args: RunArguments, *args, **kwargs):
        self.obj_name = obj_name
        self.obj = cast(TaskTemplate, obj)
        self.run_args = run_args
        super().__init__(name=obj_name, *args, **kwargs)

    def invoke(self, ctx):
        obj: CLIConfig = ctx.obj
        obj.init(self.run_args.project, self.run_args.domain)

        # todo: remove this when backend supports
        from union.storage import get_random_local_path

        run_name = "random-run-" + str(get_random_local_path())[-8:]
        if self.run_args.local:
            mode = "local"
        elif self.run_args.hybrid:
            mode = "hybrid"
            # TODO configure storage correctly for cluster
            initialize_in_cluster(storage=S3.auto())
        else:
            mode = "remote"
        logger.debug(f"Running {self.obj_name} in {mode} mode")
        r = union.with_runcontext(
            name=run_name,
            copy_style=self.run_args.copy_style,
            version=self.run_args.copy_style,
            mode=mode,
        ).run(self.obj)
        # click.secho(f"Created Run: {r.action.id}", fg="green")


class TaskPerFileGroup(common.ObjectsPerFileGroup):
    """
    Group that creates a command for each task in the current directory that is not __init__.py.
    """

    def __init__(self, filename: Path, run_args: RunArguments, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)
        self.run_args = run_args

    def _filter_objects(self, module: ModuleType) -> Dict[str, Any]:
        return {k: v for k, v in module.__dict__.items() if isinstance(v, TaskTemplate)}

    def _get_command_for_obj(self, ctx: click.Context, obj_name: str, obj: Any) -> click.Command:
        obj = cast(TaskTemplate, obj)
        return RunTaskCommand(
            obj_name=obj_name,
            obj=obj,
            help=obj.docs.__help__str__() if obj.docs else None,
            run_args=self.run_args,
        )


class TaskFiles(common.FileGroup):
    """
    Group that creates a command for each file in the current directory that is not __init__.py.
    """

    common_options_enabled = False

    def __init__(
        self,
        *args,
        directory: Path | None = None,
        **kwargs,
    ):
        if "params" not in kwargs:
            kwargs["params"] = []
        kwargs["params"].extend(RunArguments.options())
        super().__init__(*args, directory=directory, **kwargs)

    def get_command(self, ctx, filename):
        run_args = RunArguments.from_dict(ctx.params)
        fp = Path(filename)
        if not fp.exists():
            raise click.BadParameter(f"File {filename} does not exist")
        if fp.is_dir():
            return TaskFiles(directory=fp)
        return TaskPerFileGroup(
            filename=Path(filename),
            run_args=run_args,
            name=filename,
            help=f"Run, functions decorated `env.task` or instances of Tasks in {filename}",
        )


run = TaskFiles(
    name="run",
    help="Run a task from a python file",
)
