from typing import get_args

import rich_click as click

import flyte._cli._common as common
from flyte.remote._secret import SecretTypes


@click.group(name="create")
def create():
    """
    Create a new task or environment.
    """


@create.command(cls=common.CommandBase)
@click.argument("name", type=str, required=True)
@click.argument("value", type=str, required=False)
@click.option("--from-file", type=click.Path(exists=True), help="Path to the file with the binary secret.")
@click.option(
    "--type", type=click.Choice(get_args(SecretTypes)), default="regular", help="Type of the secret.", show_default=True
)
@click.pass_obj
def secret(
    cfg: common.CLIConfig,
    name: str,
    value: str | bytes | None = None,
    from_file: str | None = None,
    type: SecretTypes = "regular",
    project: str | None = None,
    domain: str | None = None,
):
    """
    Create a new secret.
    """
    from flyte.remote import Secret

    cfg.init(project, domain)
    if from_file:
        with open(from_file, "rb") as f:
            value = f.read()
    Secret.create(name=name, value=value, type=type)
