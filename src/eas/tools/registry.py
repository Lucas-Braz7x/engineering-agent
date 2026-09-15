from __future__ import annotations

from collections.abc import Callable

from eas.tools.filesystem import read_file, search_code, write_file
from eas.tools.git_tools import git_diff, git_log, git_status
from eas.tools.models import ToolContext, ToolResult
from eas.tools.shell import run_command
from eas.tools.tests_tool import run_tests
from eas.integrations.aws_tool import aws_caller_identity
from eas.integrations.ci_tool import ci_github_runs, ci_list_workflow_files
from eas.integrations.docker_tool import docker_compose_config, docker_compose_ps
from eas.integrations.github_tool import github_pr_view, github_remote_url

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
    "github_remote": "git remote URL for configured GitHub remote",
    "github_pr_view": "gh pr view (JSON summary; optional PR number)",
    "docker_compose_ps": "docker compose ps for project compose file",
    "docker_compose_services": "List compose service names",
    "aws_caller_identity": "aws sts get-caller-identity (read-only)",
    "ci_workflow_files": "List .github/workflows/*.yml",
    "ci_github_runs": "gh run list (recent CI runs)",
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
    if name == "github_remote":
        return github_remote_url(ctx)
    if name == "github_pr_view":
        pr = kwargs.get("pr_number")
        return github_pr_view(ctx, pr_number=int(pr) if pr is not None else None)
    if name == "docker_compose_ps":
        return docker_compose_ps(ctx)
    if name == "docker_compose_services":
        return docker_compose_config(ctx)
    if name == "aws_caller_identity":
        return aws_caller_identity(ctx)
    if name == "ci_workflow_files":
        return ci_list_workflow_files(ctx)
    if name == "ci_github_runs":
        return ci_github_runs(ctx, limit=int(kwargs.get("limit", 5)))
    return ToolResult(ok=False, output="", error=f"Unknown tool: {name}")
