from dataclasses import dataclass, fields
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, cast

import click

import union

from .._code_bundle._utils import CopyFiles
from . import _common as common
from ._common import CLIConfig


@dataclass
class DeployArguments:
    project: str = common.make_click_option_field(common.PROJECT_OPTION)
    domain: str = common.make_click_option_field(common.DOMAIN_OPTION)
    dry_run: bool = common.make_click_option_field(common.DRY_RUN_OPTION)
    copy_style: CopyFiles = common.make_click_option_field(
        click.Option(
            ["--copy-style"],
            type=click.Choice(["loaded_modules", "all_files", "none"]),
            default="loaded_modules",
            help="Copy style to use when running the task",
        )
    )
    version: CopyFiles = common.make_click_option_field(
        click.Option(
            ["--version"],
            type=str,
            required=False,
            help="If no files are copied, user must specify a version to register tasks with",
        )
    )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DeployArguments":
        return cls(**d)

    @classmethod
    def options(cls) -> List[click.Option]:
        """
        Return the set of base parameters added to every pyflyte run workflow subcommand.
        """
        return [common.get_option_from_metadata(f.metadata) for f in fields(cls) if f.metadata]


class DeployEnvCommand(click.Command):
    def __init__(self, obj_name: str, obj: Any, deploy_args: DeployArguments, *args, **kwargs):
        self.obj_name = obj_name
        self.obj = obj
        self.deploy_args = deploy_args
        super().__init__(name=obj_name, *args, **kwargs)

    def invoke(self, ctx):
        print(f"Deploying environment: {self.obj_name}")
        obj: CLIConfig = ctx.obj
        obj.remote_init(self.deploy_args.project, self.deploy_args.domain)
        return union.deploy(
            self.obj,
            dryrun=self.deploy_args.dry_run,
            copy_style=self.deploy_args.copy_style,
            version=self.deploy_args.version,
        )


class EnvPerFileGroup(common.ObjectsPerFileGroup):
    """
    Group that creates a command for each task in the current directory that is not __init__.py.
    """

    def __init__(self, filename: Path, deploy_args: DeployArguments, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)
        self.deploy_args = deploy_args

    def _filter_objects(self, module: ModuleType) -> Dict[str, Any]:
        return {k: v for k, v in module.__dict__.items() if isinstance(v, union.TaskEnvironment)}

    def _get_command_for_obj(self, ctx: click.Context, obj_name: str, obj: Any) -> click.Command:
        obj = cast(union.TaskEnvironment, obj)
        return DeployEnvCommand(
            obj_name=obj_name,
            obj=obj,
            help=obj.description,
            deploy_args=self.deploy_args,
        )


class EnvFiles(common.FileGroup):
    """
    Group that creates a command for each file in the current directory that is not __init__.py.
    """

    common_options_enabled = False

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        if "params" not in kwargs:
            kwargs["params"] = []
        kwargs["params"].extend(DeployArguments.options())
        super().__init__(*args, **kwargs)

    def get_command(self, ctx, filename):
        deploy_args = DeployArguments.from_dict(ctx.params)
        return EnvPerFileGroup(
            filename=Path(filename),
            deploy_args=deploy_args,
            name=filename,
            help=f"Run, functions decorated `env.task` or instances of Tasks in {filename}",
        )


deploy = EnvFiles(
    name="deploy",
    help="deploy one or more environments from a python file.",
)
