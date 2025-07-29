from typing import Any, Tuple

from union import storage
from union._context import internal_ctx
from union._datastructures import ActionID, RawDataPath
from union._internal.controllers import pbhash
from union._internal.runtime.convert import (
    Inputs,
    convert_error_to_native,
    convert_from_native_to_inputs,
    convert_outputs_to_native,
)
from union._internal.runtime.entrypoints import direct_dispatch
from union._logging import log, logger
from union._task import TaskTemplate


class LocalController:
    def __init__(self):
        logger.debug("LocalController init")

    def _get_run_params(self, inputs: Inputs) -> Tuple[ActionID, RawDataPath]:
        ctx = internal_ctx()
        parent_run = ctx.data.task_context.action
        # TODO assuming the raw_data_path is local, and for now not getting manipulated by the controller
        # We will need to change this in case of remote execution, or create data sandboxes.
        new_raw_data_path = ctx.data.raw_data_path
        # TODO ideally we should generate the name deterministically using the inputs etc
        sub_run = parent_run.new_sub_action()
        return sub_run, new_raw_data_path

    @log
    async def submit(self, _task: TaskTemplate, *args, **kwargs) -> Any:
        """
        Submit a node to the controller
        """
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
        sub_action_output_path = storage.join(current_output_path, sub_action_id.name)
        sub_action_raw_data_path = RawDataPath(path=sub_action_output_path)
        out, err = await direct_dispatch(
            _task,
            controller=self,
            action=sub_action_id,
            raw_data_path=sub_action_raw_data_path,
            inputs=inputs,
            version=tctx.version,
            checkpoints=tctx.checkpoints,
            code_bundle=tctx.code_bundle,
            output_path=sub_action_output_path,
        )
        if err:
            raise convert_error_to_native(err)
        if _task.native_interface.outputs:
            out = await convert_outputs_to_native(_task.native_interface, out)
        return out

    async def finalize_parent_action(self, action: ActionID):
        pass

    def stop(self):
        pass

    def _input_hash(self, inputs: Inputs) -> str:
        """
        Returns the hash of the inputs
        """
        return pbhash.compute_hash_string(inputs.proto_inputs)
