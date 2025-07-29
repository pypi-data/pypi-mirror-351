"""
Union runtime module, this is the entrypoint script for the Union runtime.

Caution: Startup time for this module is very important, as it is the entrypoint for the Union runtime.
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


@click.command("urun")
@click.option("--inputs", "-i", required=True)
@click.option("--outputs-path", "-o", required=True)
@click.option("--version", "-v", required=True)
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

    from union._datastructures import ActionID, Checkpoints, CodeBundle, RawDataPath
    from union._initialize import S3, initialize_in_cluster
    from union._internal.controllers import create_controller
    from union._internal.imagebuild.image_builder import ImageCache
    from union._internal.runtime.entrypoints import load_and_run_task

    if not org:
        org = "testorg"

    assert org, "Org is required for now"
    assert project, "Project is required"
    assert domain, "Domain is required"
    assert run_name, "Run name is required"
    assert name, "Action name is required"

    if run_name.startswith("{{"):
        run_name = os.environ.get("RUN_NAME")
    if name.startswith("{{"):
        name = os.environ.get("ACTION_NAME")

    bundle = CodeBundle(tgz=tgz, pkl=pkl, destination=dest, computed_version=version)
    # TODO configure storage correctly for cluster
    initialize_in_cluster(storage=S3.auto())
    controller = create_controller(ct="remote", endpoint="host.docker.internal:8090", insecure=True)

    ic = ImageCache.from_transport(image_cache) if image_cache else None

    asyncio.run(
        load_and_run_task(
            resolver=resolver,
            resolver_args=resolver_args,
            action=ActionID(name=name, run_name=run_name, project=project, domain=domain, org=org),
            raw_data_path=RawDataPath(path=raw_data_path),
            checkpoints=Checkpoints(checkpoint_path, prev_checkpoint),
            code_bundle=bundle,
            input_path=inputs,
            output_path=outputs_path,
            version=version,
            controller=controller,
            image_cache=ic,
        )
    )
