from __future__ import annotations

from pathlib import Path

from eas.integrations.proc import run_argv
from eas.tools.models import ToolContext, ToolResult


def ci_list_workflow_files(ctx: ToolContext) -> ToolResult:
    wf = ctx.root / ".github" / "workflows"
    if not wf.is_dir():
        return ToolResult(ok=False, output="", error="No .github/workflows directory")
    files = sorted(p.name for p in wf.iterdir() if p.suffix in (".yml", ".yaml"))
    if not files:
        return ToolResult(ok=False, output="", error="No workflow files found")
    return ToolResult(ok=True, output="\n".join(files))


def ci_github_runs(ctx: ToolContext, *, limit: int = 5) -> ToolResult:
    return run_argv(
        ["gh", "run", "list", "--limit", str(limit)],
        cwd=ctx.root,
    )
