from __future__ import annotations

from pathlib import Path

import typer

from eas import __version__
from eas.analysis.draft import write_minimal_draft
from eas.analysis.report import build_report
from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_MISSING_CONFIG = 2


def run_analyze(*, start_path: Path, write_draft: bool) -> int:
    root = find_repo_root(start_path)
    paths = workspace_paths(root)

    if not paths.project_yaml.is_file():
        try:
            missing = paths.project_yaml.relative_to(root)
        except ValueError:
            missing = paths.project_yaml
        typer.secho(f"Missing {missing}.", err=True)
        typer.secho(
            "Run 'engineering-agent init' to generate .ai/project.yaml, or create it manually (see docs/contexto-do-projeto.md).",
            err=True,
        )
        return EXIT_MISSING_CONFIG

    try:
        config = load_project_config(paths.project_yaml)
    except ProjectConfigError as exc:
        typer.secho(str(exc), err=True)
        return EXIT_ERROR

    if write_draft:
        draft_status = write_minimal_draft(paths)
    else:
        draft_status = "not requested"

    report = build_report(
        version=__version__,
        config=config,
        paths=paths,
        draft_status=draft_status,
    )
    typer.echo(report, nl=False)
    return EXIT_OK


def analyze(
    path: Path = typer.Option(
        Path("."),
        "--path",
        help="Project directory (repo root or subdirectory).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    write_draft: bool = typer.Option(
        False,
        "--write-draft",
        help="Create a minimal .ai/workspace/architecture.md if it does not exist.",
    ),
) -> None:
    code = run_analyze(start_path=path, write_draft=write_draft)
    if code != EXIT_OK:
        raise typer.Exit(code=code)
