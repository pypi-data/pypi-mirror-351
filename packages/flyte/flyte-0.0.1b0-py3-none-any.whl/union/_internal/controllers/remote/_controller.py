from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable

import union.storage as storage
from union._code_bundle import build_pkl_bundle
from union._context import internal_ctx
from union._datastructures import ActionID, SerializationContext
from union._internal.controllers import pbhash
from union._internal.controllers.remote._action import Action
from union._internal.controllers.remote._core import Controller
from union._internal.controllers.remote._service_protocol import ClientSet
from union._internal.runtime import io
from union._internal.runtime.convert import (
    Inputs,
    convert_error_to_native,
    convert_from_native_to_inputs,
    convert_outputs_to_native,
)
from union._internal.runtime.task_serde import translate_task_to_wire
from union._logging import logger
from union._protos.workflow import run_definition_pb2
from union._task import TaskTemplate
from union.errors import RuntimeSystemError


class RemoteController(Controller):
    """
    This a specialized controller that wraps the core controller and performs IO, serialization and deserialization
    """

    def __init__(
        self,
        client_coro: Awaitable[ClientSet],
        workers: int,
        max_system_retries: int,
        default_parent_concurrency: int = 100,
    ):
        """ """
        super().__init__(
            client_coro=client_coro,
            workers=workers,
            max_system_retries=max_system_retries,
        )
        self._default_parent_concurrency = default_parent_concurrency
        self._parent_action_semaphore = defaultdict(lambda: asyncio.Semaphore(default_parent_concurrency))

    async def _submit(self, _task: TaskTemplate, *args, **kwargs) -> Any:
        ctx = internal_ctx()
        tctx = ctx.data.task_context
        current_action_id = tctx.action
        current_output_path = tctx.output_path

        inputs = await convert_from_native_to_inputs(_task.native_interface, *args, **kwargs)
        inputs_hash = self._input_hash(inputs)
        sub_action_id = current_action_id.new_sub_action_from(
            input_hash=inputs_hash,
            group=tctx.group_data.name if tctx.group_data else None,
        )
        sub_run_output_path = storage.join(current_output_path, sub_action_id.name)
        # In the case of a regular code bundle, we will just pass it down as it is to the downstream tasks
        # It is not allowed to change the code bundle (for regular code bundles) in the middle of a run.
        code_bundle = tctx.code_bundle

        if code_bundle:
            # but if we are using a pkl bundle, we need to build a new one for the downstream tasks
            if code_bundle.pkl:
                logger.debug(f"Building new pkl bundle for task {sub_action_id.name}")
                code_bundle = await build_pkl_bundle(
                    _task,
                    upload_to_controlplane=False,
                    upload_from_dataplane_path=io.pkl_path(sub_run_output_path),
                )

        inputs_uri = io.inputs_path(sub_run_output_path)
        try:
            # TODO Add retry decorator to this
            await io.upload_inputs(inputs, inputs_uri)
        except Exception as e:
            logger.exception("Failed to upload inputs", e)
            raise RuntimeSystemError(type(e).__name__, str(e)) from e
        new_serialization_context = SerializationContext(
            project=current_action_id.project,
            domain=current_action_id.domain,
            org=current_action_id.org,
            code_bundle=code_bundle,
            version=tctx.version,
            # supplied version.
            input_path=inputs_uri,
            output_path=sub_run_output_path,
            image_cache=ctx.data.task_context.compiled_image_cache,
        )

        task_spec = translate_task_to_wire(_task, new_serialization_context)

        action = Action.from_task(
            sub_action_id=run_definition_pb2.ActionIdentifier(
                name=sub_action_id.name,
                run=run_definition_pb2.RunIdentifier(
                    name=current_action_id.run_name,
                    project=current_action_id.project,
                    domain=current_action_id.domain,
                    org=current_action_id.org,
                ),
            ),
            parent_action_name=current_action_id.name,
            group_data=tctx.group_data,
            task_spec=task_spec,
            inputs_uri=inputs_uri,
            outputs_prefix_uri=sub_run_output_path,
        )

        n = await self.submit_action(action)

        if n.has_error() or n.phase == run_definition_pb2.PHASE_FAILED:
            err = n.err or n.client_err
            if not err and n.phase == run_definition_pb2.PHASE_FAILED:
                logger.error(f"Server reported failure for action {n.action_id.name}, checking error file.")
                error_path = io.error_path(n.outputs_uri)
                # It is possible that the error file is not present in the case of a image pull failure or
                # other reasons for failure. Ideally the err message should be sent by the server, but incase its
                # missing, failed with unknown error
                try:
                    err = await io.load_error(error_path)
                except Exception as e:
                    logger.exception("Failed to load error file", e)
                    err = RuntimeSystemError(
                        type(e).__name__,
                        f"Failed to load error file: {e}",
                    )
            else:
                logger.error(f"Server reported failure for action {n.action_id.name}, error: {err}")
            raise convert_error_to_native(err)

        if _task.native_interface.outputs:
            outputs_file_path = io.outputs_path(n.outputs_uri)
            o = await io.load_outputs(outputs_file_path)
            return await convert_outputs_to_native(_task.native_interface, o)
        return None

    async def submit(self, _task: TaskTemplate, *args, **kwargs) -> Any:
        """
        Submit a task to the remote controller.This creates a new action on the queue service.
        """
        from union._context import internal_ctx

        ctx = internal_ctx()
        current_action_id = ctx.data.task_context.action
        async with self._parent_action_semaphore[current_action_id.name]:
            return await self._submit(_task, *args, **kwargs)

    async def finalize_parent_action(self, action_id: ActionID):
        """
        This method is invoked when the parent action is finished. It will finalize the run and upload the outputs
        to the control plane.
        """
        run_id = run_definition_pb2.RunIdentifier(
            name=action_id.run_name,
            project=action_id.project,
            domain=action_id.domain,
            org=action_id.org,
        )
        await super()._finalize_parent_action(run_id=run_id, parent_action_name=action_id.name)
        self._parent_action_semaphore.pop(action_id.name, None)

    def _input_hash(self, inputs: Inputs) -> str:
        return pbhash.compute_hash_string(inputs.proto_inputs)
