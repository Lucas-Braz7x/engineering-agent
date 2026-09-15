from __future__ import annotations

from pathlib import Path

import typer

from eas.context.project_yaml import write_project_yaml
from eas.detection.detect import detect_project
from eas.detection.project_root import find_project_root
from eas.store.connection import ensure_eas_dir, open_store_optional

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_EXISTS = 3


def ensure_ai_layout(root: Path) -> Path:
    ai = root / ".ai"
    ai.mkdir(exist_ok=True)
    (ai / "workspace").mkdir(exist_ok=True)
    return ai / "project.yaml"


def run_init(
    *,
    start_path: Path,
    force: bool,
    dry_run: bool,
) -> int:
    root = find_project_root(start_path)
    project_yaml = ensure_ai_layout(root) if not dry_run else root / ".ai" / "project.yaml"

    if project_yaml.is_file() and not force and not dry_run:
        typer.secho(
            f"{project_yaml.relative_to(root)} already exists. Use --force to overwrite.",
            err=True,
        )
        return EXIT_EXISTS

    result = detect_project(root)

    typer.echo("Detecting project...\n")
    if result.monorepo:
        typer.echo(f"Monorepo: {', '.join(result.manifests)}\n")
    for signal in result.signals:
        typer.echo(f"✓ {signal}")

    rel_yaml = project_yaml.relative_to(root) if project_yaml.is_relative_to(root) else project_yaml

    if dry_run:
        typer.echo(f"\n(dry-run) Would write: {rel_yaml}")
        return EXIT_OK

    write_project_yaml(project_yaml, result)
    ensure_eas_dir(root)
    if open_store_optional(root) is not None:
        typer.echo(f"Context store ready: {(root / '.eas' / 'eas.db').relative_to(root)}")
    typer.echo(f"\nProject context generated: {rel_yaml}")
    return EXIT_OK


def init(
    path: Path = typer.Option(
        Path("."),
        "--path",
        help="Directory to scan (project root or subdirectory).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing .ai/project.yaml.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print detection only; do not write files.",
    ),
) -> None:
    code = run_init(start_path=path, force=force, dry_run=dry_run)
    if code != EXIT_OK:
        raise typer.Exit(code=code)
