from __future__ import annotations

from pathlib import Path

import typer

from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths
from eas.tools.models import ToolContext, ToolResult
from eas.tools.registry import execute, list_tools

tools_app = typer.Typer(
    help="Phase 3 tools: filesystem, git, shell, tests.",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_TOOL_FAILED = 5


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


@tools_app.command("list")
def tools_list(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """List registered tools."""
    _load_ctx(path)  # validates repo-ish cwd
    for name, description in list_tools():
        typer.echo(f"{name}\t{description}")


@tools_app.command("read-file")
def tools_read_file(
    file_path: str = typer.Argument(..., help="Path relative to repo root"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "read_file", path=file_path)))


@tools_app.command("write-file")
def tools_write_file(
    file_path: str = typer.Argument(...),
    content: str = typer.Option(..., "--content", help="File content"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "write_file", path=file_path, content=content)))


@tools_app.command("search-code")
def tools_search_code(
    pattern: str = typer.Argument(..., help="Python regex"),
    glob: str = typer.Option("**/*", "--glob"),
    max_results: int = typer.Option(50, "--max"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(
        _emit(
            execute(
                ctx,
                "search_code",
                pattern=pattern,
                glob=glob,
                max_results=max_results,
            )
        )
    )


@tools_app.command("run")
def tools_run(
    command: str = typer.Argument(..., help="Command (parsed with shlex, no shell)"),
    timeout: int = typer.Option(120, "--timeout"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(
        _emit(execute(ctx, "run_command", command=command, timeout_sec=timeout))
    )


@tools_app.command("run-tests")
def tools_run_tests(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "run_tests")))


@tools_app.command("git-status")
def tools_git_status(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "git_status")))


@tools_app.command("git-log")
def tools_git_log(
    max_count: int = typer.Option(10, "-n", "--max"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "git_log", max_count=max_count)))


@tools_app.command("git-diff")
def tools_git_diff(
    base: str | None = typer.Option(None, "--base", help="e.g. main"),
    head: str | None = typer.Option(None, "--head", help="e.g. HEAD"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    ctx = _load_ctx(path)
    raise typer.Exit(_emit(execute(ctx, "git_diff", base=base, head=head)))
