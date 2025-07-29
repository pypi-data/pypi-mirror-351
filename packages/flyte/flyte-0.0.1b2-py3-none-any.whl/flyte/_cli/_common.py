from __future__ import annotations

import importlib.util
import logging
import os
import sys
from abc import abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, Dict, Iterable, List, Optional

import rich.box
import rich_click as click
from rich.panel import Panel
from rich.table import Table

import flyte.errors

PREFERRED_BORDER_COLOR = "dim cyan"
PREFERRED_ACCENT_COLOR = "bold #FFD700"
HEADER_STYLE = f"{PREFERRED_ACCENT_COLOR} on black"

PROJECT_OPTION = click.Option(
    param_decls=["-p", "--project"],
    required=False,
    type=str,
    default="default",
    help="Project to operate on",
    show_default=True,
)

DOMAIN_OPTION = click.Option(
    param_decls=["-d", "--domain"],
    required=False,
    type=str,
    default="development",
    help="Domain to operate on",
    show_default=True,
)

DRY_RUN_OPTION = click.Option(
    param_decls=["--dry-run", "--dryrun"],
    required=False,
    type=bool,
    is_flag=True,
    default=False,
    help="Dry run, do not actually call the backend service.",
    show_default=True,
)


def _common_options() -> List[click.Option]:
    """
    Common options for that will be added to all commands and groups that inherit from CommandBase or GroupBase.
    """
    return [PROJECT_OPTION, DOMAIN_OPTION]


# This is global state for the CLI, it is manipulated by the main command


@dataclass(frozen=True)
class CLIConfig:
    """
    This is the global state for the CLI. It is manipulated by the main command.
    """

    log_level: int | None = logging.ERROR
    endpoint: str | None = None
    insecure: bool = False
    org_override: str | None = None

    def replace(self, **kwargs) -> CLIConfig:
        """
        Replace the global state with a new one.
        """
        return replace(self, **kwargs)

    def init(self, project: str | None = None, domain: str | None = None):
        import flyte

        flyte.init(
            endpoint=self.endpoint,
            insecure=self.insecure,
            org=self.org_override,
            project=project,
            domain=domain,
            log_level=self.log_level,
        )


class InvokeBaseMixin:
    """
    Mixin to catch grpc.RpcError, flyte.RpcError, other errors and other exceptions and raise them as
     gclick.ClickException.
    """

    def invoke(self, ctx):
        import grpc

        try:
            return super().invoke(ctx)  # type: ignore
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise click.ClickException(f"Authentication failed. Please check your credentials. {e.details()}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise click.ClickException(f"Requested object NOT FOUND. Please check your input. Error: {e.details()}")
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise click.ClickException("Resource already exists.")
            raise click.ClickException(f"RPC error invoking command: {e!s}") from e
        except flyte.errors.InitializationError:
            raise click.ClickException("Initialize the CLI with a remote configuration. For example, pass --endpoint")
        except Exception as e:
            raise click.ClickException(f"Error invoking command: {e}") from e


class CommandBase(InvokeBaseMixin, click.RichCommand):
    """
    Base class for all commands, that adds common options to all commands if enabled.
    """

    common_options_enabled = True

    def __init__(self, *args, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = []
        if self.common_options_enabled:
            kwargs["params"].extend(_common_options())
        super().__init__(*args, **kwargs)


class GroupBase(InvokeBaseMixin, click.RichGroup):
    """
    Base class for all commands, that adds common options to all commands if enabled.
    """

    common_options_enabled = True

    def __init__(self, *args, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = []
        if self.common_options_enabled:
            kwargs["params"].extend(_common_options())
        super().__init__(*args, **kwargs)


class GroupBaseNoOptions(GroupBase):
    common_options_enabled = False


def get_option_from_metadata(metadata: MappingProxyType) -> click.Option:
    return metadata["click.option"]


def key_value_callback(_: Any, param: str, values: List[str]) -> Optional[Dict[str, str]]:
    """
    Callback for click to parse key-value pairs.
    """
    if not values:
        return None
    result = {}
    for v in values:
        if "=" not in v:
            raise click.BadParameter(f"Expected key-value pair of the form key=value, got {v}")
        k, v_ = v.split("=", 1)
        result[k.strip()] = v_.strip()
    return result


class ObjectsPerFileGroup(GroupBase):
    """
    Group that creates a command for each object in a python file.
    """

    def __init__(self, filename: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not filename.exists():
            raise click.ClickException(f"{filename} does not exists")
        self.filename = filename
        self._objs: Dict[str, Any] | None = None

    @abstractmethod
    def _filter_objects(self, module: ModuleType) -> Dict[str, Any]:
        """
        Filter the objects in the module to only include the ones we want to expose.
        """
        raise NotImplementedError

    @property
    def objs(self) -> Dict[str, Any]:
        if self._objs is not None:
            return self._objs

        module_name = os.path.splitext(os.path.basename(self.filename))[0]
        module_path = os.path.dirname(os.path.abspath(self.filename))

        spec = importlib.util.spec_from_file_location(module_name, self.filename)
        if spec is None or spec.loader is None:
            raise click.ClickException(f"Could not load module {module_name} from {self.filename}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        sys.path.append(module_path)
        spec.loader.exec_module(module)

        self._objs = self._filter_objects(module)
        if not self._objs:
            raise click.ClickException(f"No objects found in {self.filename}")
        return self._objs

    def list_commands(self, ctx):
        m = list(self.objs.keys())
        return sorted(m)

    @abstractmethod
    def _get_command_for_obj(self, ctx: click.Context, obj_name: str, obj: Any) -> click.Command: ...

    def get_command(self, ctx, obj_name):
        obj = self.objs[obj_name]
        return self._get_command_for_obj(ctx, obj_name, obj)


class FileGroup(GroupBase):
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
        super().__init__(*args, **kwargs)
        self._files = None
        self._dir = directory

    @property
    def files(self):
        if self._files is None:
            directory = self._dir or Path(".").absolute()
            self._files = [os.fspath(p) for p in directory.glob("*.py") if p.name != "__init__.py"]
        return self._files

    def list_commands(self, ctx):
        return self.files

    def get_command(self, ctx, filename):
        raise NotImplementedError


def get_table(title: str, vals: Iterable[Any]) -> Table:
    """
    Get a table from a list of values.
    """
    table = Table(
        title=title,
        box=rich.box.SQUARE_DOUBLE_HEAD,
        header_style=HEADER_STYLE,
        show_header=True,
        border_style=PREFERRED_BORDER_COLOR,
    )
    headers = None
    for p in vals:
        if headers is None:
            headers = [k for k, _ in p.__rich_repr__()]
            for h in headers:
                table.add_column(h.capitalize())
        table.add_row(*[str(v) for _, v in p.__rich_repr__()])
    return table


def get_panel(title: str, renderable: Any) -> Panel:
    """
    Get a panel from a list of values.
    """
    return Panel.fit(
        renderable,
        title=f"[{PREFERRED_ACCENT_COLOR}]{title}[/{PREFERRED_ACCENT_COLOR}]",
        border_style=PREFERRED_BORDER_COLOR,
    )
