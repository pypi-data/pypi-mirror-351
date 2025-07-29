from __future__ import annotations

import pathlib
import uuid
from typing import TYPE_CHECKING, Literal, Optional, Union

from union import S3

from ._api_commons import syncer
from ._context import internal_ctx, contextual_run
from ._datastructures import ActionID, Checkpoints, RawDataPath, SerializationContext
from ._initialize import get_client, get_common_config, requires_initialization, initialize_in_cluster
from ._internal import create_controller
from ._internal.runtime.io import upload_inputs, _INPUTS_FILE_NAME, _CHECKPOINT_FILE_NAME
from ._internal.runtime.taskrunner import extract_download_run_upload
from ._logging import logger
from ._task import P, R, TaskTemplate
from ._tools import ipython_check
from .errors import InitializationError

if TYPE_CHECKING:
    from union.remote import Run

    from ._code_bundle import CopyFiles

Mode = Literal["local", "remote", "hybrid"]


@syncer.wrap
class _Runner:
    def __init__(
        self,
        force_mode: Mode | None = None,
        name: Optional[str] = None,
        service_account: Optional[str] = None,
        version: Optional[str] = None,
        copy_style: CopyFiles = "loaded_modules",
        dry_run: bool = False,
        copy_bundle_to: pathlib.Path | None = None,
        interactive_mode: bool | None = None,
        raw_data_path: str | None = None,
        metadata_path: str | None = None,
    ):
        if not force_mode and get_client() is not None:
            force_mode = "remote"
        force_mode = force_mode or "local"
        logger.debug(f"Effective run mode: {force_mode}, client configured: {get_client() is not None}")
        self._mode = force_mode
        self._name = name
        self._service_account = service_account
        self._version = version
        self._copy_files = copy_style
        self._dry_run = dry_run
        self._copy_bundle_to = copy_bundle_to
        self._interactive_mode = interactive_mode if interactive_mode else ipython_check()
        self._raw_data_path = raw_data_path
        self._metadata_path = metadata_path or "/tmp"

    @requires_initialization
    async def _run_remote(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> Run:
        from union.remote import Run

        from ._code_bundle import build_code_bundle, build_pkl_bundle
        from ._deploy import build_images, plan_deploy
        from ._internal.runtime.convert import convert_from_native_to_inputs
        from ._internal.runtime.task_serde import translate_task_to_wire
        from ._protos.workflow import run_definition_pb2, run_service_pb2

        cfg = get_common_config()

        deploy_plan = plan_deploy(obj.parent_env())
        image_cache = await build_images(deploy_plan)

        if self._interactive_mode:
            code_bundle = await build_pkl_bundle(
                obj, upload_to_controlplane=not self._dry_run, copy_bundle_to=self._copy_bundle_to
            )
        else:
            if self._copy_files != "none":
                code_bundle = await build_code_bundle(
                    from_dir=cfg.root_dir, dryrun=self._dry_run, copy_bundle_to=self._copy_bundle_to
                )
            else:
                code_bundle = None

        version = self._version or (
            code_bundle.computed_version if code_bundle and code_bundle.computed_version else None
        )
        if not version:
            raise ValueError("Version is required when running a task")
        s_ctx = SerializationContext(
            code_bundle=code_bundle,
            version=version,
            image_cache=image_cache,
        )
        task_spec = translate_task_to_wire(obj, s_ctx)
        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)

        if not self._dry_run:
            if get_client() is None:
                # This can only happen, if the user forces union.run(mode="remote") without initializing the client
                raise InitializationError(
                    "ClientNotInitializedError",
                    "user",
                    "union.run requires client to be initialized. "
                    "Call union.init() with a valid endpoint or api-key before using this function.",
                )
            run_id = run_definition_pb2.RunIdentifier(
                project=cfg.project,
                domain=cfg.domain,
                org=cfg.org,  # todo: this should be removed
                name=self._name if self._name else None,
            )
            # Fill in task id inside the task template if it's not provided.
            # Maybe this should be done here, or the backend.
            if task_spec.task_template.id.project == "":
                task_spec.task_template.id.project = cfg.project if cfg.project else ""
            if task_spec.task_template.id.domain == "":
                task_spec.task_template.id.domain = cfg.domain if cfg.domain else ""
            if task_spec.task_template.id.org == "":
                task_spec.task_template.id.org = cfg.org if cfg.org else ""
            if task_spec.task_template.id.version == "":
                task_spec.task_template.id.version = version
            resp = await get_client().run_service.CreateRun(
                run_service_pb2.CreateRunRequest(
                    run_id=run_id,
                    task_spec=task_spec,
                    inputs=inputs.proto_inputs,
                ),
            )
            return Run(pb2=resp.run)

        class DryRun(Run):
            def __init__(self, _task_spec, _inputs, _code_bundle):
                super().__init__(
                    pb2=run_definition_pb2.Run(
                        action=run_definition_pb2.Action(
                            id=run_definition_pb2.ActionIdentifier(
                                name="a0", run=run_definition_pb2.RunIdentifier(name="dry-run")
                            )
                        )
                    )
                )
                self.task_spec = _task_spec
                self.inputs = _inputs
                self.code_bundle = _code_bundle

        return DryRun(_task_spec=task_spec, _inputs=inputs, _code_bundle=code_bundle)

    @requires_initialization
    async def _run_hybrid(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        from ._code_bundle import build_code_bundle, build_pkl_bundle
        from ._deploy import build_images, plan_deploy
        from ._internal.runtime.convert import convert_from_native_to_inputs
        from ._internal.runtime.task_serde import translate_task_to_wire

        cfg = get_common_config()

        deploy_plan = plan_deploy(obj.parent_env())
        image_cache = await build_images(deploy_plan)

        if self._interactive_mode:
            code_bundle = await build_pkl_bundle(
                obj, upload_to_controlplane=not self._dry_run, copy_bundle_to=self._copy_bundle_to
            )
        else:
            if self._copy_files != "none":
                code_bundle = await build_code_bundle(
                    from_dir=cfg.root_dir, dryrun=self._dry_run, copy_bundle_to=self._copy_bundle_to
                )
            else:
                code_bundle = None

        version = self._version or (
            code_bundle.computed_version if code_bundle and code_bundle.computed_version else None
        )
        if not version:
            raise ValueError("Version is required when running a task")
        # s_ctx = SerializationContext(
        #     code_bundle=code_bundle,
        #     version=version,
        #     image_cache=image_cache,
        # )
        # task_spec = translate_task_to_wire(obj, s_ctx)

        project = cfg.project or "testproject"
        domain = cfg.domain or "development"
        org = cfg.org or "testorg"
        action_name = self._name or "a0"
        run_name = "random-run-90d88ae7"
        random_id = str(uuid.uuid4())[:6]

        controller = create_controller(ct="remote", endpoint="localhost:8090", insecure=True)
        action = ActionID(name=action_name, run_name=run_name, project=project, domain=domain, org=org)

        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)
        output_path = f"s3://bucket/metadata/v2/{org}/{project}/{domain}/{run_name}/{action_name}"
        raw_data_path = f"{output_path}/rd/{random_id}"
        input_path = f"{raw_data_path}/{_INPUTS_FILE_NAME}"
        checkpoint_path = f"{raw_data_path}/{_CHECKPOINT_FILE_NAME}"
        prev_checkpoint = f"{raw_data_path}/prev_checkpoint"
        checkpoints = Checkpoints(checkpoint_path, prev_checkpoint)
        await upload_inputs(inputs, input_path)

        await contextual_run(
            extract_download_run_upload,
            obj,
            action=action,
            version=version,
            controller=controller,
            raw_data_path=raw_data_path,
            output_path=output_path,
            checkpoints=checkpoints,
            code_bundle=code_bundle,
            input_path=input_path,
            image_cache=image_cache,
        )

    async def _run_local(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        from union._internal.controllers import create_controller
        from union._internal.runtime.convert import (
            convert_error_to_native,
            convert_from_native_to_inputs,
            convert_outputs_to_native,
        )
        from union._internal.runtime.entrypoints import direct_dispatch

        controller = create_controller(ct="local")

        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)
        if self._name is None:
            action = ActionID.create_random()
        else:
            action = ActionID(name=self._name)
        out, err = await direct_dispatch(
            obj,
            action=action,
            raw_data_path=internal_ctx().raw_data,
            version="na",
            controller=controller,
            inputs=inputs,
            output_path=self._metadata_path,
            checkpoints=Checkpoints(
                prev_checkpoint_path=internal_ctx().raw_data.path, checkpoint_path=internal_ctx().raw_data.path
            ),
        )  # type: ignore
        if err:
            raise convert_error_to_native(err)
        return await convert_outputs_to_native(obj.native_interface, out)

    async def _run_local(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        from union._internal.controllers import create_controller
        from union._internal.runtime.convert import (
            convert_error_to_native,
            convert_from_native_to_inputs,
            convert_outputs_to_native,
        )
        from union._internal.runtime.entrypoints import direct_dispatch

        controller = create_controller(ct="local")

        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)
        if self._name is None:
            action = ActionID.create_random()
        else:
            action = ActionID(name=self._name)
        out, err = await direct_dispatch(
            obj,
            action=action,
            raw_data_path=internal_ctx().raw_data,
            version="na",
            controller=controller,
            inputs=inputs,
            output_path=self._metadata_path,
            checkpoints=Checkpoints(
                prev_checkpoint_path=internal_ctx().raw_data.path, checkpoint_path=internal_ctx().raw_data.path
            ),
        )  # type: ignore
        if err:
            raise convert_error_to_native(err)
        return await convert_outputs_to_native(obj.native_interface, out)

    async def run(self, task: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> Union[R, Run]:
        """
        Run an async `@env.task` or `TaskTemplate` instance. The existing async context will be used.

        Example:
        ```python
        import union
        env = union.TaskEnvironment("example")

        @env.task
        async def example_task(x: int, y: str) -> str:
            return f"{x} {y}"

        if __name__ == "__main__":
            union.run(example_task, 1, y="hello")
        ```

        :param task: TaskTemplate instance `@env.task` or `TaskTemplate`
        :param args: Arguments to pass to the Task
        :param kwargs: Keyword arguments to pass to the Task
        :return: Run instance or the result of the task
        """
        if self._mode == "remote":
            return await self._run_remote(task, *args, **kwargs)
        if self._mode == "hybrid":
            return await self._run_hybrid(task, *args, **kwargs)

        # TODO We could use this for remote as well and users could simply pass union:// or s3:// or file://
        async with internal_ctx().new_raw_data_path(
            raw_data_path=RawDataPath.from_local_folder(local_folder=self._raw_data_path)
        ):
            return await self._run_local(task, *args, **kwargs)


def with_runcontext(
    mode: Mode | None = None,
    *,
    name: Optional[str] = None,
    service_account: Optional[str] = None,
    version: Optional[str] = None,
    copy_style: CopyFiles = "loaded_modules",
    dry_run: bool = False,
    copy_bundle_to: pathlib.Path | None = None,
    interactive_mode: bool | None = None,
    raw_data_path: str | None = None,
) -> _Runner:
    """
    Launch a new run with the given parameters as the context.

    Example:
    ```python
    import union
    env = union.TaskEnvironment("example")

    @env.task
    async def example_task(x: int, y: str) -> str:
        return f"{x} {y}"

    if __name__ == "__main__":
        union.with_runcontext(name="example_run_id").run(example_task, 1, y="hello")
    ```

    :param mode: Optional The mode to use for the run, if not provided, it will be computed from union.init
    :param version: Optional The version to use for the run, if not provided, it will be computed from the code bundle
    :param name: Optional The name to use for the run
    :param service_account: Optional The service account to use for the run context
    :param copy_style: Optional The copy style to use for the run context
    :param dry_run: Optional If true, the run will not be executed, but the bundle will be created
    :param copy_bundle_to: When dry_run is True, the bundle will be copied to this location if specified
    :param interactive_mode: Optional, can be forced to True or False.
         If not provided, it will be set based on the current environment. For example Jupyter notebooks are considered
         interactive mode, while scripts are not. This is used to determine how the code bundle is created.
    :param raw_data_path: Use this path to store the raw data for the run. Currently only supported for local runs,
      and can be used to store raw data in specific locations. TODO coming soon for remote runs as well.
    :return: runner
    """
    return _Runner(
        force_mode=mode,
        name=name,
        service_account=service_account,
        version=version,
        copy_style=copy_style,
        dry_run=dry_run,
        copy_bundle_to=copy_bundle_to,
        interactive_mode=interactive_mode,
        raw_data_path=raw_data_path,
    )


@syncer.wrap
async def run(task: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> Union[R, Run]:
    return await _Runner().run.aio(task, *args, **kwargs)
