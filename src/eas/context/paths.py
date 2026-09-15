from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path
    project_yaml: Path
    requirement_md: Path
    architecture_md: Path


def find_repo_root(start: Path) -> Path:
    """Walk upward until a directory containing `.ai/` is found."""
    current = start.resolve()
    for directory in (current, *current.parents):
        if (directory / ".ai").is_dir():
            return directory
    return current


def workspace_paths(root: Path) -> WorkspacePaths:
    ai = root / ".ai"
    workspace = ai / "workspace"
    return WorkspacePaths(
        root=root,
        project_yaml=ai / "project.yaml",
        requirement_md=workspace / "requirement.md",
        architecture_md=workspace / "architecture.md",
    )
