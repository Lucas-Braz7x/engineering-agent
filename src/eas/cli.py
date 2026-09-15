from __future__ import annotations

import typer

from eas import __version__
from eas.commands.analyze import analyze
from eas.commands.init import init
from eas.commands.tools_cmd import tools_app
from eas.commands.integrations_cmd import integrations_app
from eas.commands.loop_cmd import loop
from eas.commands.workflow_cmds import bug, feature, review, status

app = typer.Typer(
    name="engineering-agent",
    help="Engineering Agent System CLI.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show package version.",
    ),
) -> None:
    """Engineering Agent System CLI."""


app.command("init")(init)
app.command("analyze")(analyze)
app.add_typer(tools_app, name="tools")
app.add_typer(integrations_app, name="integrations")
app.command("feature")(feature)
app.command("review")(review)
app.command("bug")(bug)
app.command("status")(status)
app.command("loop")(loop)
