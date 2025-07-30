import asyncio
import dataclasses
import datetime
import enum
import importlib
import importlib.util
import json
import os
import pathlib
import sys
import typing
import typing as t
from typing import get_args

import rich_click as click
import yaml
from flyteidl.core.literals_pb2 import Literal
from flyteidl.core.types_pb2 import BlobType, LiteralType, SimpleType

from union._logging import logger
from union.io import Dir, File
from union.io.pickle.transformer import FlytePickleTransformer
from union.storage._remote_fs import RemoteFSPathResolver
from union.types import TypeEngine


# ---------------------------------------------------
# TODO replace these
class ArtifactQuery:
    pass


def is_remote(v: str) -> bool:
    return False


class StructuredDataset:
    def __init__(self, uri: str | None = None, dataframe: typing.Any = None):
        self.uri = uri
        self.dataframe = dataframe


# ---------------------------------------------------


def is_pydantic_basemodel(python_type: typing.Type) -> bool:
    """
    Checks if the python type is a pydantic BaseModel
    """
    try:
        import pydantic  # noqa: F401
    except ImportError:
        return False
    else:
        try:
            from pydantic import BaseModel as BaseModelV2
            from pydantic.v1 import BaseModel as BaseModelV1

            return issubclass(python_type, BaseModelV1) or issubclass(python_type, BaseModelV2)
        except ImportError:
            from pydantic import BaseModel

        return issubclass(python_type, BaseModel)


def key_value_callback(_: typing.Any, param: str, values: typing.List[str]) -> typing.Optional[typing.Dict[str, str]]:
    """
    Callback for click to parse key-value pairs.
    """
    if not values:
        return None
    result = {}
    for v in values:
        if "=" not in v:
            raise click.BadParameter(f"Expected key-value pair of the form key=value, got {v}")
        k, val = v.split("=", 1)
        result[k.strip()] = val.strip()
    return result


def labels_callback(_: typing.Any, param: str, values: typing.List[str]) -> typing.Optional[typing.Dict[str, str]]:
    """
    Callback for click to parse labels.
    """
    if not values:
        return None
    result = {}
    for v in values:
        if "=" not in v:
            result[v.strip()] = ""
        else:
            k, val = v.split("=", 1)
            result[k.strip()] = val.strip()
    return result


class DirParamType(click.ParamType):
    name = "directory path"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value

        # set remote_directory to false if running pyflyte run locally. This makes sure that the original
        # directory is used and not a random one.
        remote_directory = None if getattr(ctx.obj, "is_remote", False) else False
        if not is_remote(value):
            p = pathlib.Path(value)
            if not p.exists() or not p.is_dir():
                raise click.BadParameter(f"parameter should be a valid flytedirectory path, {value}")
        return Dir(path=value, remote_directory=remote_directory)


class StructuredDatasetParamType(click.ParamType):
    """
    TODO handle column types
    """

    name = "structured dataset path (dir/file)"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value
        if isinstance(value, str):
            return StructuredDataset(uri=value)
        elif isinstance(value, StructuredDataset):
            return value
        return StructuredDataset(dataframe=value)


class FileParamType(click.ParamType):
    name = "file path"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value
        # set remote_directory to false if running pyflyte run locally. This makes sure that the original
        # file is used and not a random one.
        remote_path = None if getattr(ctx.obj, "is_remote", False) else False
        if not is_remote(value):
            p = pathlib.Path(value)
            if not p.exists() or not p.is_file():
                raise click.BadParameter(f"parameter should be a valid file path, {value}")
        return File(path=value, remote_path=remote_path)


class PickleParamType(click.ParamType):
    name = "pickle"

    def get_metavar(self, param: click.Parameter) -> t.Optional[str]:
        return "Python Object <Module>:<Object>"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if not isinstance(value, str):
            return value
        parts = value.split(":")
        if len(parts) != 2:
            if ctx and ctx.obj and ctx.obj.verbose > 0:
                click.echo(f"Did not receive a string in the expected format <MODULE>:<VAR>, falling back to: {value}")
            return value
        try:
            sys.path.insert(0, os.getcwd())
            m = importlib.import_module(parts[0])
            return m.__getattribute__(parts[1])
        except ModuleNotFoundError as e:
            raise click.BadParameter(f"Failed to import module {parts[0]}, error: {e}")
        except AttributeError as e:
            raise click.BadParameter(f"Failed to find attribute {parts[1]} in module {parts[0]}, error: {e}")


class JSONIteratorParamType(click.ParamType):
    name = "json iterator"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        return value


import re


def parse_iso8601_duration(iso_duration: str) -> datetime.timedelta:
    pattern = re.compile(
        r"^P"  # Starts with 'P'
        r"(?:(?P<days>\d+)D)?"  # Optional days
        r"(?:T"  # Optional time part
        r"(?:(?P<hours>\d+)H)?"
        r"(?:(?P<minutes>\d+)M)?"
        r"(?:(?P<seconds>\d+)S)?"
        r")?$"
    )
    match = pattern.match(iso_duration)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration format: {iso_duration}")

    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    return datetime.timedelta(**parts)


def parse_human_durations(text: str) -> list[datetime.timedelta]:
    raw_parts = text.strip("[]").split("|")
    durations = []

    for part in raw_parts:
        part = part.strip().lower()

        # Match 1:24 or :45
        m_colon = re.match(r"^(?:(\d+):)?(\d+)$", part)
        if m_colon:
            minutes = int(m_colon.group(1)) if m_colon.group(1) else 0
            seconds = int(m_colon.group(2))
            durations.append(datetime.timedelta(minutes=minutes, seconds=seconds))
            continue

        # Match "10 days", "1 minute", etc.
        m_units = re.match(r"^(\d+)\s*(day|hour|minute|second)s?$", part)
        if m_units:
            value = int(m_units.group(1))
            unit = m_units.group(2)
            durations.append(datetime.timedelta(**{unit + "s": value}))
            continue

        print(f"Warning: could not parse '{part}'")

    return durations


def parse_duration(s: str) -> datetime.timedelta:
    try:
        return parse_iso8601_duration(s)
    except ValueError:
        parts = parse_human_durations(s)
        if not parts:
            raise ValueError(f"Could not parse duration: {s}")
        return sum(parts, datetime.timedelta())


class DateTimeType(click.DateTime):
    _NOW_FMT = "now"
    _TODAY_FMT = "today"
    _FIXED_FORMATS: typing.ClassVar[typing.List[str]] = [_NOW_FMT, _TODAY_FMT]
    _FLOATING_FORMATS: typing.ClassVar[typing.List[str]] = ["<FORMAT> - <ISO8601 duration>"]
    _ADDITONAL_FORMATS: typing.ClassVar[typing.List[str]] = [*_FIXED_FORMATS, *_FLOATING_FORMATS]
    _FLOATING_FORMAT_PATTERN = r"(.+)\s+([-+])\s+(.+)"

    def __init__(self):
        super().__init__()
        self.formats.extend(self._ADDITONAL_FORMATS)

    def _datetime_from_format(
        self, value: str, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> datetime.datetime:
        if value in self._FIXED_FORMATS:
            if value == self._NOW_FMT:
                return datetime.datetime.now()
            if value == self._TODAY_FMT:
                n = datetime.datetime.now()
                return datetime.datetime(n.year, n.month, n.day)
        return super().convert(value, param, ctx)

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value

        if isinstance(value, str) and " " in value:
            import re

            m = re.match(self._FLOATING_FORMAT_PATTERN, value)
            if m:
                parts = m.groups()
                if len(parts) != 3:
                    raise click.BadParameter(f"Expected format <FORMAT> - <ISO8601 duration>, got {value}")
                dt = self._datetime_from_format(parts[0], param, ctx)
                try:
                    delta = parse_duration(parts[2])
                except Exception as e:
                    raise click.BadParameter(
                        f"Matched format {self._FLOATING_FORMATS}, but failed to parse duration {parts[2]}, error: {e}"
                    )
                if parts[1] == "-":
                    return dt - delta
                return dt + delta
            else:
                value = datetime.datetime.fromisoformat(value)

        return self._datetime_from_format(value, param, ctx)


class DurationParamType(click.ParamType):
    name = "[1:24 | :22 | 1 minute | 10 days | ...]"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value
        if value is None:
            raise click.BadParameter("None value cannot be converted to a Duration type.")
        return parse_duration(value)


class EnumParamType(click.Choice):
    def __init__(self, enum_type: typing.Type[enum.Enum]):
        super().__init__([str(e.value) for e in enum_type])
        self._enum_type = enum_type

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> enum.Enum:
        if isinstance(value, ArtifactQuery):
            return value
        if isinstance(value, self._enum_type):
            return value
        return self._enum_type(super().convert(value, param, ctx))


class UnionParamType(click.ParamType):
    """
    A composite type that allows for multiple types to be specified. This is used for union types.
    """

    def __init__(self, types: typing.List[click.ParamType]):
        super().__init__()
        self._types = self._sort_precedence(types)

    @property
    def name(self) -> str:
        return "|".join([t.name for t in self._types])

    @staticmethod
    def _sort_precedence(tp: typing.List[click.ParamType]) -> typing.List[click.ParamType]:
        unprocessed = []
        str_types = []
        others = []
        for p in tp:
            if isinstance(p, type(click.UNPROCESSED)):
                unprocessed.append(p)
            elif isinstance(p, type(click.STRING)):
                str_types.append(p)
            else:
                others.append(p)
        return others + str_types + unprocessed

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        """
        Important to implement NoneType / Optional.
        Also could we just determine the click types from the python types
        """
        if isinstance(value, ArtifactQuery):
            return value
        for p in self._types:
            try:
                return p.convert(value, param, ctx)
            except Exception as e:
                logger.debug(f"Ignoring conversion error for type {p} trying other variants in Union. Error: {e}")
        raise click.BadParameter(f"Failed to convert {value} to any of the types {self._types}")


class JsonParamType(click.ParamType):
    name = "json object OR json/yaml file path"

    def __init__(self, python_type: typing.Type):
        super().__init__()
        self._python_type = python_type

    def _parse(self, value: typing.Any, param: typing.Optional[click.Parameter]):
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except Exception:
            try:
                # We failed to load the json, so we'll try to load it as a file
                if os.path.exists(value):
                    # if the value is a yaml file, we'll try to load it as yaml
                    if value.endswith(".yaml") or value.endswith(".yml"):
                        with open(value, "r") as f:
                            return yaml.safe_load(f)
                    with open(value, "r") as f:
                        return json.load(f)
                raise
            except json.JSONDecodeError as e:
                raise click.BadParameter(f"parameter {param} should be a valid json object, {value}, error: {e}")

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value
        if value is None:
            raise click.BadParameter("None value cannot be converted to a Json type.")

        parsed_value = self._parse(value, param)

        # We compare the origin type because the json parsed value for list or dict is always a list or dict without
        # the covariant type information.
        if type(parsed_value) == typing.get_origin(self._python_type) or type(parsed_value) == self._python_type:
            # Indexing the return value of get_args will raise an error for native dict and list types.
            # We don't support native list/dict types with nested dataclasses.
            if get_args(self._python_type) == ():
                return parsed_value
            elif isinstance(parsed_value, list) and dataclasses.is_dataclass(get_args(self._python_type)[0]):
                j = JsonParamType(get_args(self._python_type)[0])
                return [j.convert(v, param, ctx) for v in parsed_value]
            elif isinstance(parsed_value, dict) and dataclasses.is_dataclass(get_args(self._python_type)[1]):
                j = JsonParamType(get_args(self._python_type)[1])
                return {k: j.convert(v, param, ctx) for k, v in parsed_value.items()}

            return parsed_value

        if is_pydantic_basemodel(self._python_type):
            """
            This function supports backward compatibility for the Pydantic v1 plugin.
            If the class is a Pydantic BaseModel, it attempts to parse JSON input using
            the appropriate version of Pydantic (v1 or v2).
            """
            try:
                if importlib.util.find_spec("pydantic.v1") is not None:
                    from pydantic import BaseModel as BaseModelV2

                    if issubclass(self._python_type, BaseModelV2):
                        return self._python_type.model_validate_json(
                            json.dumps(parsed_value), strict=False, context={"deserialize": True}
                        )
            except ImportError:
                pass

            # The behavior of the Pydantic v1 plugin.
            return self._python_type.parse_raw(json.dumps(parsed_value))
        return None


def modify_literal_uris(lit: Literal):
    """
    Modifies the literal object recursively to replace the URIs with the native paths.
    """
    if lit.collection:
        for l in lit.collection.literals:
            modify_literal_uris(l)
    elif lit.map:
        for k, v in lit.map.literals.items():
            modify_literal_uris(v)
    elif lit.scalar:
        if lit.scalar.blob and lit.scalar.blob.uri and lit.scalar.blob.uri.startswith(RemoteFSPathResolver.protocol):
            lit.scalar.blob._uri = RemoteFSPathResolver.resolve_remote_path(lit.scalar.blob.uri)
        elif lit.scalar.union:
            modify_literal_uris(lit.scalar.union.value)
        elif (
            lit.scalar.structured_dataset
            and lit.scalar.structured_dataset.uri
            and lit.scalar.structured_dataset.uri.startswith(RemoteFSPathResolver.protocol)
        ):
            lit.scalar.structured_dataset._uri = RemoteFSPathResolver.resolve_remote_path(
                lit.scalar.structured_dataset.uri
            )


SIMPLE_TYPE_CONVERTER: typing.Dict[SimpleType, click.ParamType] = {
    SimpleType.FLOAT: click.FLOAT,
    SimpleType.INTEGER: click.INT,
    SimpleType.STRING: click.STRING,
    SimpleType.BOOLEAN: click.BOOL,
    SimpleType.DURATION: DurationParamType(),
    SimpleType.DATETIME: DateTimeType(),
}


def literal_type_to_click_type(lt: LiteralType, python_type: typing.Type) -> click.ParamType:
    """
    Converts a Flyte LiteralType given a python_type to a click.ParamType
    """
    if lt.simple:
        if lt.simple == SimpleType.STRUCT:
            ct = JsonParamType(python_type)
            ct.name = f"JSON object {python_type.__name__}"
            return ct
        if lt.simple in SIMPLE_TYPE_CONVERTER:
            return SIMPLE_TYPE_CONVERTER[lt.simple]
        raise NotImplementedError(f"Type {lt.simple} is not supported in pyflyte run")

    if lt.enum_type:
        return EnumParamType(python_type)  # type: ignore

    if lt.structured_dataset_type:
        return StructuredDatasetParamType()

    if lt.collection_type or lt.map_value_type:
        ct = JsonParamType(python_type)
        if lt.collection_type:
            ct.name = "json list"
        else:
            ct.name = "json dictionary"
        return ct

    if lt.blob:
        if lt.blob.dimensionality == BlobType.BlobDimensionality.SINGLE:
            if lt.blob.format == FlytePickleTransformer.PYTHON_PICKLE_FORMAT:
                return PickleParamType()
            # elif lt.blob.format == JSONIteratorTransformer.JSON_ITERATOR_FORMAT:
            #     return JSONIteratorParamType()
            return FileParamType()
        return DirParamType()

    if lt.union_type:
        cts = []
        for i in range(len(lt.union_type.variants)):
            variant = lt.union_type.variants[i]
            variant_python_type = typing.get_args(python_type)[i]
            ct = literal_type_to_click_type(variant, variant_python_type)
            cts.append(ct)
        return UnionParamType(cts)

    return click.UNPROCESSED


class FlyteLiteralConverter(object):
    name = "literal_type"

    def __init__(
        self,
        literal_type: LiteralType,
        python_type: typing.Type,
        is_remote: bool,
    ):
        self._is_remote = is_remote
        self._literal_type = literal_type
        self._python_type = python_type
        self._click_type = literal_type_to_click_type(literal_type, python_type)

    @property
    def click_type(self) -> click.ParamType:
        return self._click_type

    def is_bool(self) -> bool:
        return self.click_type == click.BOOL

    def convert(
        self, ctx: click.Context, param: typing.Optional[click.Parameter], value: typing.Any
    ) -> typing.Union[Literal, typing.Any]:
        """
        Convert the value to a Flyte Literal or a python native type. This is used by click to convert the input.
        """
        if isinstance(value, ArtifactQuery):
            return value
        try:
            # If the expected Python type is datetime.date, adjust the value to date
            if self._python_type is datetime.date:
                # Click produces datetime, so converting to date to avoid type mismatch error
                value = value.date()
            # If the input matches the default value in the launch plan, serialization can be skipped.
            if param and value == param.default:
                return None

            # If this is used for remote execution, then we need to convert it back to a python native type
            if not self._is_remote:
                return value

            lit = asyncio.run(TypeEngine.to_literal(value, self._python_type, self._literal_type))
            return lit
        except click.BadParameter:
            raise
        except Exception as e:
            raise click.BadParameter(
                f"Failed to convert param: {param if param else 'NA'}, value: {value} to type: {self._python_type}."
                f" Reason {e}"
            ) from e
