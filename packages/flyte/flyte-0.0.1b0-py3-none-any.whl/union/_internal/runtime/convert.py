from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from flyteidl.core import execution_pb2, literals_pb2

import union.errors
from union._datastructures import NativeInterface
from union._protos.workflow import run_definition_pb2
from union.types import TypeEngine


@dataclass(frozen=True)
class Inputs:
    proto_inputs: run_definition_pb2.Inputs


@dataclass(frozen=True)
class Outputs:
    proto_outputs: run_definition_pb2.Outputs


@dataclass
class Error:
    err: execution_pb2.ExecutionError


# ------------------------------- CONVERT Methods ------------------------------- #


def _clean_error_code(code: str) -> Tuple[str, str | None]:
    """
    The error code may have a server injected code and is of the form `RetriesExhausedError|<code>` or `<code>`.

    :param code:
    :return: "user code", optional server code
    """
    if "|" in code:
        server_code, user_code = code.split("|", 1)
        return user_code.strip(), server_code.strip()
    return code.strip(), None


async def convert_inputs_to_native(inputs: Inputs, python_interface: NativeInterface) -> Dict[str, Any]:
    literals = {named_literal.name: named_literal.value for named_literal in inputs.proto_inputs.literals}
    inputs = await TypeEngine.literal_map_to_kwargs(
        literals_pb2.LiteralMap(literals=literals), python_interface.get_input_types()
    )
    return inputs


async def convert_from_native_to_inputs(interface: NativeInterface, *args, **kwargs) -> Inputs:
    kwargs = interface.convert_to_kwargs(*args, **kwargs)
    literal_map = await TypeEngine.dict_to_literal_map(kwargs, interface.get_input_types())
    return Inputs(
        proto_inputs=run_definition_pb2.Inputs(
            literals=[run_definition_pb2.NamedLiteral(name=k, value=v) for k, v in literal_map.literals.items()]
        )
    )


async def convert_from_native_to_outputs(o: Any, interface: NativeInterface) -> Outputs:
    # Always make it a tuple even if it's just one item to simplify logic below
    if not isinstance(o, tuple):
        o = (o,)

    assert len(interface.outputs) == len(interface.outputs), (
        f"Received {len(o)} outputs but interface has {len(interface.outputs)}"
    )
    named = []
    for (output_name, python_type), v in zip(interface.outputs.items(), o):
        lit = await TypeEngine.to_literal(v, python_type, TypeEngine.to_literal_type(python_type))
        named.append(run_definition_pb2.NamedLiteral(name=output_name, value=lit))

    return Outputs(proto_outputs=run_definition_pb2.Outputs(literals=named))


async def convert_outputs_to_native(interface: NativeInterface, outputs: Outputs) -> Union[Any, Tuple[Any, ...]]:
    lm = literals_pb2.LiteralMap(
        literals={named_literal.name: named_literal.value for named_literal in outputs.proto_outputs.literals}
    )
    kwargs = await TypeEngine.literal_map_to_kwargs(lm, interface.outputs)
    if len(kwargs) == 0:
        return None
    elif len(kwargs) == 1:
        return next(iter(kwargs.values()))
    else:
        # Return as tuple if multiple outputs, make sure to order correctly as it seems proto maps can change ordering
        return tuple(kwargs[k] for k in interface.outputs.keys())


def convert_error_to_native(err: execution_pb2.ExecutionError | Exception | Error) -> BaseException | None:
    if not err:
        return None

    if isinstance(err, Exception):
        return err

    if isinstance(err, Error):
        err = err.err

    user_code, server_code = _clean_error_code(err.code)
    match err.kind:
        case execution_pb2.ExecutionError.UNKNOWN:
            return union.errors.RuntimeUnknownError(code=user_code, message=err.message, worker=err.worker)
        case execution_pb2.ExecutionError.USER:
            if "OOM" in err.code.upper():
                return union.errors.OOMError(code=user_code, message=err.message, worker=err.worker)
            elif "Interrupted" in err.code:
                return union.errors.TaskInterruptedError(code=user_code, message=err.message, worker=err.worker)
            elif "PrimaryContainerNotFound" in err.code:
                return union.errors.PrimaryContainerNotFoundError(
                    code=user_code, message=err.message, worker=err.worker
                )
            elif "RetriesExhausted" in err.code:
                return union.errors.RetriesExhaustedError(code=user_code, message=err.message, worker=err.worker)
            elif "Unknown" in err.code:
                return union.errors.RuntimeUnknownError(code=user_code, message=err.message, worker=err.worker)
            elif "InvalidImageName" in err.code:
                return union.errors.InvalidImageNameError(code=user_code, message=err.message, worker=err.worker)
            elif "ImagePullBackOff" in err.code:
                return union.errors.ImagePullBackOffError(code=user_code, message=err.message, worker=err.worker)
            return union.errors.RuntimeUserError(code=user_code, message=err.message, worker=err.worker)
        case execution_pb2.ExecutionError.SYSTEM:
            return union.errors.RuntimeSystemError(code=user_code, message=err.message, worker=err.worker)


def convert_from_native_to_error(err: BaseException) -> Error:
    if isinstance(err, union.errors.RuntimeUnknownError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.UNKNOWN,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    elif isinstance(err, union.errors.RuntimeUserError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.USER,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    elif isinstance(err, union.errors.RuntimeSystemError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.SYSTEM,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    else:
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.UNKNOWN,
                code=type(err).__name__,
                message=str(err),
                worker="UNKNOWN",
            )
        )
