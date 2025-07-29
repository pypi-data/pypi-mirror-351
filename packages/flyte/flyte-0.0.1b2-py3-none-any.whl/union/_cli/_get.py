import asyncio

import rich_click as click
from rich.console import Console

from . import _common as common


@click.group(name="get")
def get():
    """
    Get the value of a task or environment.
    """


@get.command()
@click.argument("name", type=str, required=False)
@click.pass_obj
def project(cfg: common.CLIConfig, name: str | None = None):
    """
    Get the current project.
    """
    from union.remote import Project

    print(cfg)
    cfg.init()

    console = Console()
    if name:
        console.print(Project.get(name))
    else:
        console.print(common.get_table("Projects", Project.listall()))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.pass_obj
def run(cfg: common.CLIConfig, name: str | None = None, project: str | None = None, domain: str | None = None):
    """
    Get the current run.
    """
    from union.remote import Run, RunDetails

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        details = RunDetails.get(name=name)
        console.print(details)
    else:
        console.print(common.get_table("Runs", Run.listall()))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.argument("version", type=str, required=False)
@click.pass_obj
def task(
    cfg: common.CLIConfig,
    name: str | None = None,
    version: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get the current task.
    """
    from union.remote import Task

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        v = Task.get(name=name, version=version)
        if v is None:
            raise click.BadParameter(f"Task {name} not found.")
        t = v.fetch()
        console.print(t)
    else:
        raise click.BadParameter("Task listing is not supported yet, please provide a name.")
        # console.print(common.get_table("Tasks", Task.listall()))


@get.command(cls=common.CommandBase)
@click.argument("run_name", type=str, required=True)
@click.argument("action_name", type=str, required=False)
@click.pass_obj
def action(
    cfg: common.CLIConfig,
    run_name: str,
    action_name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get all actions for a run or details for a specific action.
    """
    import union.remote as remote

    cfg.init(project=project, domain=domain)

    console = Console()
    if action_name:
        console.print(remote.Action.get(run_name=run_name, name=action_name))
    else:
        # List all actions for the run
        console.print(common.get_table(f"Actions for {run_name}", remote.Action.listall(for_run_name=run_name)))


@get.command(cls=common.CommandBase)
@click.argument("run_name", type=str, required=False)
@click.argument("action_name", type=str, required=False)
@click.pass_obj
def logs(
    cfg: common.CLIConfig,
    run_name: str,
    action_name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get the current run.
    """
    import union.remote as remote

    cfg.init(project=project, domain=domain)

    async def _run_log_view(_obj):
        task = asyncio.create_task(_obj.show_logs())
        try:
            await task
        except KeyboardInterrupt:
            task.cancel()

    if action_name:
        obj = remote.Action.get(run_name=run_name, name=action_name)
    else:
        obj = remote.Run.get(run_name)
    asyncio.run(_run_log_view(obj))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.pass_obj
def secret(
    cfg: common.CLIConfig,
    name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get the current secret.
    """
    import union.remote as remote

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        console.print(remote.Secret.get(name))
    else:
        console.print(common.get_table("Secrets", remote.Secret.listall()))
