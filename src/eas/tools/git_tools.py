from __future__ import annotations

import subprocess

from eas.tools.models import ToolContext, ToolResult
from eas.tools.shell import DEFAULT_TIMEOUT_SEC, MAX_OUTPUT_BYTES


def _git(ctx: ToolContext, *args: str) -> ToolResult:
    if not (ctx.root / ".git").exists():
        return ToolResult(ok=False, output="", error="Not a git repository")

    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ctx.root,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SEC,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    out = (completed.stdout or "") + (
        f"\n--- stderr ---\n{completed.stderr}" if completed.stderr else ""
    )
    out = out.strip()
    if len(out.encode("utf-8")) > MAX_OUTPUT_BYTES:
        out = out[:MAX_OUTPUT_BYTES] + "\n... (truncated)"

    ok = completed.returncode == 0
    return ToolResult(
        ok=ok,
        output=out,
        error=None if ok else f"git exited {completed.returncode}",
        exit_code=completed.returncode,
    )


def git_status(ctx: ToolContext) -> ToolResult:
    return _git(ctx, "status", "--short", "--branch")


def git_log(ctx: ToolContext, *, max_count: int = 10) -> ToolResult:
    return _git(
        ctx,
        "log",
        f"-{max_count}",
        "--oneline",
        "--decorate",
    )


def git_diff(
    ctx: ToolContext,
    *,
    base: str | None = None,
    head: str | None = None,
) -> ToolResult:
    if base is None and head is None:
        return _git(ctx, "diff")
    if base and head:
        return _git(ctx, "diff", base, head)
    if base:
        return _git(ctx, "diff", base)
    return _git(ctx, "diff", head or "HEAD")
