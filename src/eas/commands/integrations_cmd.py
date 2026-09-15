from __future__ import annotations

from pathlib import Path

import typer

from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths
from eas.integrations.detect import detect_integration_signals
from eas.tools.models import ToolContext, ToolResult
from eas.tools.registry import execute

integrations_app = typer.Typer(
    help="Phase 6: GitHub, Docker, AWS, CI (read-only).",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_INTEGRATION = 8


def _ctx(start: Path) -> ToolContext:
    root = find_repo_root(start)
    paths = workspace_paths(root)
    config = None
    if paths.project_yaml.is_file():
        config = load_project_config(paths.project_yaml)
    return ToolContext(root=root, config=config)


def _emit(result: ToolResult) -> int:
    if result.output:
        typer.echo(result.output, nl=not result.output.endswith("\n"))
    if result.ok:
        return EXIT_OK
    if result.error:
        typer.secho(result.error, err=True)
    return EXIT_INTEGRATION


@integrations_app.command("status")
def integrations_status(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Detect integration signals in the repo (no external calls)."""
    root = find_repo_root(path)
    typer.echo("Integration signals:\n")
    signals = detect_integration_signals(root)
    if not signals:
        typer.echo("  (none detected)")
        raise typer.Exit(EXIT_OK)
    for signal in signals:
        typer.echo(f"  ✓ {signal}")
    raise typer.Exit(EXIT_OK)


@integrations_app.command("github")
def integrations_github(
    pr: int | None = typer.Option(None, "--pr", help="PR number"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _ctx(path)
    remote = execute(ctx, "github_remote")
    if remote.ok:
        typer.echo(f"remote: {remote.output}\n")
    else:
        typer.secho(remote.error or "remote failed", err=True)
    if pr is not None:
        raise typer.Exit(_emit(execute(ctx, "github_pr_view", pr_number=pr)))
    raise typer.Exit(_emit(execute(ctx, "github_pr_view")))


@integrations_app.command("docker")
def integrations_docker(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _ctx(path)
    services = execute(ctx, "docker_compose_services")
    if services.ok:
        typer.echo("Services:")
        typer.echo(services.output)
    else:
        typer.secho(services.error or "compose services failed", err=True)
    raise typer.Exit(_emit(execute(ctx, "docker_compose_ps")))


@integrations_app.command("aws")
def integrations_aws(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _ctx(path)
    raise typer.Exit(_emit(execute(ctx, "aws_caller_identity")))


@integrations_app.command("ci")
def integrations_ci(
    limit: int = typer.Option(5, "--limit"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _ctx(path)
    files = execute(ctx, "ci_workflow_files")
    if files.ok:
        typer.echo("Workflow files:")
        typer.echo(files.output)
        typer.echo("")
    else:
        typer.secho(files.error or "", err=True)
    raise typer.Exit(_emit(execute(ctx, "ci_github_runs", limit=limit)))
