from __future__ import annotations

from typing import Optional

import typer

from eas import __version__
from eas.commands.analyze import analyze

app = typer.Typer(
    name="engineering-agent",
    help="Engineering Agent System — Phase 0 CLI.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show package version.",
    ),
) -> None:
    """Engineering Agent System CLI."""


app.command("analyze")(analyze)
