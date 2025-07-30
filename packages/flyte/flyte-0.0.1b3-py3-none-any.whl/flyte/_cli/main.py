import rich_click as click

from ._common import CLIConfig
from ._create import create
from ._deploy import deploy
from ._get import get
from ._run import run


def _verbosity_to_loglevel(verbosity: int) -> int | None:
    """
    Converts a verbosity level from the CLI to a logging level.

    :param verbosity: verbosity level from the CLI
    :return: logging level
    """
    import logging

    match verbosity:
        case 0:
            return None
        case 1:
            return logging.WARNING
        case 2:
            return logging.INFO
        case _:
            return logging.DEBUG


@click.group(cls=click.RichGroup)
@click.option(
    "--endpoint",
    type=str,
    required=False,
    help="The endpoint to connect to, this will override any config and simply used pkce to connect.",
)
@click.option(
    "--insecure",
    is_flag=True,
    required=False,
    help="insecure",
    type=bool,
    default=False,
)
@click.option(
    "-v",
    "--verbose",
    required=False,
    help="Show verbose messages and exception traces",
    count=True,
    default=0,
    type=int,
)
@click.option(
    "--org-override",
    type=str,
    required=False,
    help="Override for org",
)
@click.pass_context
def main(ctx: click.Context, endpoint: str | None, insecure: bool, verbose: int, org_override: str | None):
    """
    v2 cli. Root command, please use one of the subcommands.
    """
    log_level = _verbosity_to_loglevel(verbose)
    ctx.obj = CLIConfig(log_level=log_level, endpoint=endpoint, insecure=insecure, org_override=org_override)


main.add_command(run)
main.add_command(deploy)
main.add_command(get)  # type: ignore
main.add_command(create)  # type: ignore
