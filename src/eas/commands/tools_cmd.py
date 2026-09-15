from __future__ import annotations

from pathlib import Path

import typer

from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths
from eas.tools.models import ToolContext, ToolResult
from eas.runtime.load_agent import AgentLoadError, load_agent
from eas.tools.registry import execute, list_tools

tools_app = typer.Typer(
    help="Phase 3 tools: filesystem, git, shell, tests.",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_TOOL_FAILED = 5


@tools_app.callback()
def tools_callback(
    ctx: typer.Context,
    agent: str | None = typer.Option(
        None,
        "--agent",
        help="Enforce role tool policy for this agent id",
    ),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx.ensure_object(dict)
    manifest = None
    if agent:
        root = find_repo_root(path)
        try:
            manifest = load_agent(root, agent)
        except AgentLoadError as exc:
            typer.secho(str(exc), err=True)
            raise typer.Exit(EXIT_TOOL_FAILED)
    ctx.obj["agent"] = manifest
    ctx.obj["root"] = find_repo_root(path)


def _agent_from_ctx(ctx: typer.Context):
    return (ctx.obj or {}).get("agent")


def _repo_root(ctx: typer.Context, path: Path | None) -> Path:
    if path is not None:
        return find_repo_root(path)
    return ctx.obj["root"]


def _load_ctx(start_path: Path) -> ToolContext:
    root = find_repo_root(start_path)
    paths = workspace_paths(root)
    config = None
    if paths.project_yaml.is_file():
        try:
            config = load_project_config(paths.project_yaml)
        except ProjectConfigError:
            config = None
    return ToolContext(root=root, config=config)


def _emit(result: ToolResult) -> int:
    if result.output:
        typer.echo(result.output, nl=not result.output.endswith("\n"))
    if result.ok:
        return EXIT_OK
    if result.error:
        typer.secho(result.error, err=True)
    return EXIT_TOOL_FAILED


_PATH_OPT = typer.Option(
    None,
    "--path",
    exists=True,
    file_okay=False,
    dir_okay=True,
    help="Repository path (default: cwd)",
)


@tools_app.command("list")
def tools_list(ctx: typer.Context, path: Path | None = _PATH_OPT) -> None:
    """List registered tools."""
    root = _repo_root(ctx, path)
    _load_ctx(root)
    manifest = _agent_from_ctx(ctx)
    for name, description in list_tools():
        if manifest is not None and name not in manifest.allowed_tools:
            continue
        typer.echo(f"{name}\t{description}")


@tools_app.command("read-file")
def tools_read_file(
    ctx: typer.Context,
    file_path: str = typer.Argument(..., help="Path relative to repo root"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(execute(tool_ctx, "read_file", agent=_agent_from_ctx(ctx), path=file_path))
    )


@tools_app.command("write-file")
def tools_write_file(
    ctx: typer.Context,
    file_path: str = typer.Argument(...),
    content: str = typer.Option(..., "--content", help="File content"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(
                tool_ctx,
                "write_file",
                agent=_agent_from_ctx(ctx),
                path=file_path,
                content=content,
            )
        )
    )


@tools_app.command("write-artifact")
def tools_write_artifact(
    ctx: typer.Context,
    content: str = typer.Option(..., "--content", help="Artifact markdown body"),
    artifact_path: str | None = typer.Option(
        None,
        "--artifact-path",
        help="Defaults to agent artifact_path from manifest",
    ),
    path: Path | None = _PATH_OPT,
) -> None:
    """Write agent artifact (requires --agent on parent command)."""
    manifest = _agent_from_ctx(ctx)
    if manifest is None:
        typer.secho("write-artifact requires: tools --agent <id> write-artifact ...", err=True)
        raise typer.Exit(EXIT_TOOL_FAILED)
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(
                tool_ctx,
                "write_artifact",
                agent=manifest,
                path=artifact_path or manifest.artifact_path,
                content=content,
            )
        )
    )


@tools_app.command("search-code")
def tools_search_code(
    ctx: typer.Context,
    pattern: str = typer.Argument(..., help="Python regex"),
    glob: str = typer.Option("**/*", "--glob"),
    max_results: int = typer.Option(50, "--max"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(
                tool_ctx,
                "search_code",
                agent=_agent_from_ctx(ctx),
                pattern=pattern,
                glob=glob,
                max_results=max_results,
            )
        )
    )


@tools_app.command("run")
def tools_run(
    ctx: typer.Context,
    command: str = typer.Argument(..., help="Command (parsed with shlex, no shell)"),
    timeout: int = typer.Option(120, "--timeout"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(
                tool_ctx,
                "run_command",
                agent=_agent_from_ctx(ctx),
                command=command,
                timeout_sec=timeout,
            )
        )
    )


@tools_app.command("run-tests")
def tools_run_tests(ctx: typer.Context, path: Path | None = _PATH_OPT) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(execute(tool_ctx, "run_tests", agent=_agent_from_ctx(ctx)))
    )


@tools_app.command("git-status")
def tools_git_status(ctx: typer.Context, path: Path | None = _PATH_OPT) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(execute(tool_ctx, "git_status", agent=_agent_from_ctx(ctx)))
    )


@tools_app.command("git-log")
def tools_git_log(
    ctx: typer.Context,
    max_count: int = typer.Option(10, "-n", "--max"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(tool_ctx, "git_log", agent=_agent_from_ctx(ctx), max_count=max_count)
        )
    )


@tools_app.command("git-diff")
def tools_git_diff(
    ctx: typer.Context,
    base: str | None = typer.Option(None, "--base", help="e.g. main"),
    head: str | None = typer.Option(None, "--head", help="e.g. HEAD"),
    path: Path | None = _PATH_OPT,
) -> None:
    tool_ctx = _load_ctx(_repo_root(ctx, path))
    raise typer.Exit(
        _emit(
            execute(
                tool_ctx,
                "git_diff",
                agent=_agent_from_ctx(ctx),
                base=base,
                head=head,
            )
        )
    )
