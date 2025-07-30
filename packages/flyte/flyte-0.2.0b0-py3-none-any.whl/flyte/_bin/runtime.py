"""
Flyte runtime module, this is the entrypoint script for the Flyte runtime.

Caution: Startup time for this module is very important, as it is the entrypoint for the Flyte runtime.
Refrain from importing any modules here. If you need to import any modules, do it inside the main function.
"""

import asyncio
import os
import sys
from typing import List

import click

# Todo: work with pvditt to make these the names
# ACTION_NAME = "_U_ACTION_NAME"
# RUN_NAME = "_U_RUN_NAME"
# PROJECT_NAME = "_U_PROJECT_NAME"
# DOMAIN_NAME = "_U_DOMAIN_NAME"
# ORG_NAME = "_U_ORG_NAME"

ACTION_NAME = "ACTION_NAME"
RUN_NAME = "RUN_NAME"
PROJECT_NAME = "FLYTE_INTERNAL_TASK_PROJECT"
DOMAIN_NAME = "FLYTE_INTERNAL_TASK_DOMAIN"
ORG_NAME = "_U_ORG_NAME"
ENDPOINT_OVERRIDE = "_U_EP_OVERRIDE"
RUN_OUTPUT_BASE_DIR = "_U_RUN_BASE"


@click.command("a0")
@click.option("--inputs", "-i", required=True)
@click.option("--outputs-path", "-o", required=True)
@click.option("--version", "-v", required=True)
@click.option("--run-base-dir", envvar=RUN_OUTPUT_BASE_DIR, required=True)
@click.option("--raw-data-path", "-r", required=False)
@click.option("--checkpoint-path", "-c", required=False)
@click.option("--prev-checkpoint", "-p", required=False)
@click.option("--name", envvar=ACTION_NAME, required=False)
@click.option("--run-name", envvar=RUN_NAME, required=False)
@click.option("--project", envvar=PROJECT_NAME, required=False)
@click.option("--domain", envvar=DOMAIN_NAME, required=False)
@click.option("--org", envvar=ORG_NAME, required=False)
@click.option("--image-cache", required=False)
@click.option("--tgz", required=False)
@click.option("--pkl", required=False)
@click.option("--dest", required=False)
@click.option("--resolver", required=False)
@click.argument(
    "resolver-args",
    type=click.UNPROCESSED,
    nargs=-1,
)
def main(
    run_name: str,
    name: str,
    project: str,
    domain: str,
    org: str,
    image_cache: str,
    version: str,
    inputs: str,
    run_base_dir: str,
    outputs_path: str,
    raw_data_path: str,
    checkpoint_path: str,
    prev_checkpoint: str,
    tgz: str,
    pkl: str,
    dest: str,
    resolver: str,
    resolver_args: List[str],
):
    sys.path.insert(0, ".")

    import flyte._utils as utils
    from flyte._datastructures import ActionID, Checkpoints, CodeBundle, RawDataPath
    from flyte._initialize import S3, initialize_in_cluster
    from flyte._internal.controllers import create_controller
    from flyte._internal.imagebuild.image_builder import ImageCache
    from flyte._internal.runtime.entrypoints import load_and_run_task

    assert org, "Org is required for now"
    assert project, "Project is required"
    assert domain, "Domain is required"
    assert run_name, f"Run name is required {run_name}"
    assert name, f"Action name is required {name}"

    if run_name.startswith("{{"):
        run_name = os.getenv("RUN_NAME", "")
    if name.startswith("{{"):
        name = os.getenv("ACTION_NAME", "")

    ep = os.environ.get(ENDPOINT_OVERRIDE, "host.docker.internal:8090")

    bundle = CodeBundle(tgz=tgz, pkl=pkl, destination=dest, computed_version=version)
    # TODO configure storage correctly for cluster
    initialize_in_cluster(storage=S3.auto())
    controller = create_controller(ct="remote", endpoint=ep, insecure=True)

    ic = ImageCache.from_transport(image_cache) if image_cache else None

    # Create a coroutine to load the task and run it
    task_coroutine = load_and_run_task(
        resolver=resolver,
        resolver_args=resolver_args,
        action=ActionID(name=name, run_name=run_name, project=project, domain=domain, org=org),
        raw_data_path=RawDataPath(path=raw_data_path),
        checkpoints=Checkpoints(checkpoint_path, prev_checkpoint),
        code_bundle=bundle,
        input_path=inputs,
        output_path=outputs_path,
        run_base_dir=run_base_dir,
        version=version,
        controller=controller,
        image_cache=ic,
    )
    # Create a coroutine to watch for errors
    controller_failure = controller.watch_for_errors()

    # Run both coroutines concurrently and wait for first to finish and cancel the other
    async def _run_and_stop():
        await utils.run_coros(controller_failure, task_coroutine)
        await controller.stop()

    asyncio.run(_run_and_stop())
