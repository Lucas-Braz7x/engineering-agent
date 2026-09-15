from __future__ import annotations

from collections.abc import Callable

from eas.tools.filesystem import read_file, search_code, write_file
from eas.tools.git_tools import git_diff, git_log, git_status
from eas.tools.models import ToolContext, ToolResult
from eas.tools.shell import run_command
from eas.tools.tests_tool import run_tests

ToolFn = Callable[[ToolContext], ToolResult]

# Names use underscores — stable contract for Phase 4 agents.
TOOL_CATALOG: dict[str, str] = {
    "read_file": "Read a UTF-8 text file under the repository root",
    "write_file": "Write a UTF-8 text file (blocked under .git)",
    "search_code": "Regex search across files (skips .git, node_modules, venv)",
    "run_command": "Run a shell-free command with cwd = repo root",
    "run_tests": "Run testing.command from .ai/project.yaml",
    "git_diff": "git diff (default: unstaged/staged vs HEAD)",
    "git_status": "git status --short --branch",
    "git_log": "git log --oneline",
}


def list_tools() -> list[tuple[str, str]]:
    return sorted(TOOL_CATALOG.items())


def execute(ctx: ToolContext, name: str, **kwargs) -> ToolResult:
    if name == "read_file":
        return read_file(ctx, path=kwargs["path"])
    if name == "write_file":
        return write_file(ctx, path=kwargs["path"], content=kwargs["content"])
    if name == "search_code":
        return search_code(
            ctx,
            pattern=kwargs["pattern"],
            glob=kwargs.get("glob", "**/*"),
            max_results=int(kwargs.get("max_results", 50)),
        )
    if name == "run_command":
        return run_command(
            ctx,
            command=kwargs["command"],
            timeout_sec=int(kwargs.get("timeout_sec", 120)),
        )
    if name == "run_tests":
        return run_tests(ctx)
    if name == "git_status":
        return git_status(ctx)
    if name == "git_log":
        return git_log(ctx, max_count=int(kwargs.get("max_count", 10)))
    if name == "git_diff":
        return git_diff(
            ctx,
            base=kwargs.get("base"),
            head=kwargs.get("head"),
        )
    return ToolResult(ok=False, output="", error=f"Unknown tool: {name}")
