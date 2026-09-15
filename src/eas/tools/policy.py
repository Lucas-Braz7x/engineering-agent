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


def normalize_repo_relative(path: str) -> str:
    return Path(path).as_posix().lstrip("./")


def assert_artifact_write_path(path: str, artifact_path: str) -> None:
    """Only agent artifact or run-scoped markdown under .ai/workspace/runs/."""
    norm = normalize_repo_relative(path)
    art = normalize_repo_relative(artifact_path)
    if norm == art:
        return
    if norm.startswith(".ai/workspace/runs/") and norm.endswith(".md"):
        return
    raise ToolPolicyError(
        f"write_artifact blocked for {path!r}: must be {artifact_path!r} "
        "or .ai/workspace/runs/<run-id>/*.md"
    )
