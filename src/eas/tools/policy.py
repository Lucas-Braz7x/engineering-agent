from __future__ import annotations

from pathlib import Path

from eas.tools.errors import ToolPolicyError

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".eggs",
}


def resolve_repo_path(root: Path, relative: str) -> Path:
    """Resolve a user path relative to repo root; block escape."""
    root_resolved = root.resolve()
    candidate = Path(relative)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root_resolved / candidate).resolve()

    if not resolved.is_relative_to(root_resolved):
        raise ToolPolicyError(f"Path escapes repository root: {relative}")
    return resolved


def assert_writable(path: Path, root: Path) -> None:
    resolved = path.resolve()
    root_resolved = root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ToolPolicyError("Path escapes repository root")
    if ".git" in resolved.parts:
        raise ToolPolicyError("Writing under .git is not allowed")


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES
