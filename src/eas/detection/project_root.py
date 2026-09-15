from __future__ import annotations

from pathlib import Path

MANIFEST_MARKERS = (
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "requirements.txt",
)


def find_project_root(start: Path) -> Path:
    """Walk upward; return the nearest directory that looks like a project root."""
    current = start.resolve()
    for directory in (current, *current.parents):
        if any((directory / name).is_file() for name in MANIFEST_MARKERS):
            return directory
        if (directory / ".git").exists():
            return directory
    return current
