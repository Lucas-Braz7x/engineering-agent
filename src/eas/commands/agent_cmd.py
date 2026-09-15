from __future__ import annotations

from pathlib import Path

import typer

from eas.runtime.load_agent import AgentLoadError, load_agent
from eas.runtime.roles import AGENT_ROLE_POLICIES, CODER_ROLE, TOOL_ALIASES, denied_tools_for_policy
from eas.runtime.validate_artifact import validate_artifact
from eas.context.paths import find_repo_root

agent_app = typer.Typer(
    help="Agent roles, tool permissions, and artifact validation.",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_AGENT_ERROR = 4


@agent_app.command("list")
def agent_list(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """List agents with review peer pairs."""
    root = find_repo_root(path)
    for agent_id in sorted(AGENT_ROLE_POLICIES):
        try:
            manifest = load_agent(root, agent_id)
        except AgentLoadError:
            manifest = None
        policy = AGENT_ROLE_POLICIES[agent_id]
        peer = manifest.review_peer if manifest else policy.review_peer
        typer.echo(f"{agent_id}\tpeer={peer or '-'}")


@agent_app.command("show")
def agent_show(
    agent_id: str = typer.Argument(..., help="e.g. architect"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Show allowed/denied tools and required outputs for an agent."""
    root = find_repo_root(path)
    try:
        agent = load_agent(root, agent_id)
    except AgentLoadError as exc:
        typer.secho(str(exc), err=True)
        raise typer.Exit(EXIT_AGENT_ERROR)

    denied = sorted(denied_tools_for_policy(AGENT_ROLE_POLICIES[agent_id]))
    typer.echo(f"Agent: {agent.id}")
    typer.echo(f"Role: {agent.role_id}")
    typer.echo(f"Review peer: {agent.review_peer or '(none)'}")
    typer.echo(f"Artifact: {agent.artifact_path}")
    typer.echo("\nAllowed tools:")
    for name in sorted(agent.allowed_tools):
        typer.echo(f"  - {name}")
    typer.echo("\nDenied tools:")
    for name in denied:
        typer.echo(f"  - {name}")
    typer.echo("\nRequired H2 sections (strict validation):")
    for section in agent.required_sections:
        typer.echo(f"  - {section}")
    typer.echo("\nRequired eas-artifact YAML keys:")
    for key in agent.required_yaml_keys:
        typer.echo(f"  - {key}")
    typer.echo("\nTool aliases (documentation):")
    for alias, target in TOOL_ALIASES.items():
        typer.echo(f"  - {alias} -> {target}")


@agent_app.command("validate")
def agent_validate(
    agent_id: str = typer.Argument(...),
    artifact: Path = typer.Argument(..., help="Path to artifact markdown"),
    strict: bool = typer.Option(False, "--strict", help="Also require H2 sections"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Validate an artifact file against agent output schema."""
    root = find_repo_root(path)
    try:
        agent = load_agent(root, agent_id)
    except AgentLoadError as exc:
        typer.secho(str(exc), err=True)
        raise typer.Exit(EXIT_AGENT_ERROR)

    if not artifact.is_file():
        typer.secho(f"Not a file: {artifact}", err=True)
        raise typer.Exit(EXIT_ERROR)

    text = artifact.read_text(encoding="utf-8")
    errors = validate_artifact(text, agent, check_sections=strict)
    if errors:
        typer.secho("Validation failed:", err=True)
        for err in errors:
            typer.secho(f"  - {err}", err=True)
        raise typer.Exit(EXIT_AGENT_ERROR)
    typer.echo("OK")


@agent_app.command("coder-profile")
def agent_coder_profile() -> None:
    """Show the coder role profile (implementer; not a bundled agent yet)."""
    typer.echo(f"Role: {CODER_ROLE.role_id}")
    typer.echo(CODER_ROLE.summary)
    typer.echo(f"Review peer: {CODER_ROLE.review_peer}")
    typer.echo("Allowed tools:")
    for name in sorted(CODER_ROLE.allowed_tools):
        typer.echo(f"  - {name}")
