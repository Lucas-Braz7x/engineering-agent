from __future__ import annotations

import json
import subprocess

from eas.context.integrations_config import IntegrationsConfig
from eas.integrations.proc import run_argv
from eas.tools.models import ToolContext, ToolResult


def _integrations(ctx: ToolContext) -> IntegrationsConfig:
    if ctx.config and ctx.config.integrations:
        return ctx.config.integrations
    return IntegrationsConfig()


def github_pr_view(ctx: ToolContext, *, pr_number: int | None = None) -> ToolResult:
    args = ["gh", "pr", "view", "--json", "title,state,url,headRefName,baseRefName"]
    if pr_number is not None:
        args.insert(2, str(pr_number))
    result = run_argv(args, cwd=ctx.root)
    if not result.ok:
        return result
    try:
        data = json.loads(result.output)
        lines = [
            f"title: {data.get('title')}",
            f"state: {data.get('state')}",
            f"url: {data.get('url')}",
            f"branch: {data.get('headRefName')} → {data.get('baseRefName')}",
        ]
        return ToolResult(ok=True, output="\n".join(lines))
    except json.JSONDecodeError:
        return result


def github_remote_url(ctx: ToolContext) -> ToolResult:
    remote = _integrations(ctx).github_remote
    try:
        completed = subprocess.run(
            ["git", "remote", "get-url", remote],
            cwd=ctx.root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return ToolResult(ok=False, output="", error=str(exc))
    if completed.returncode != 0:
        return ToolResult(ok=False, output="", error=completed.stderr or f"remote {remote} missing")
    return ToolResult(ok=True, output=completed.stdout.strip())
