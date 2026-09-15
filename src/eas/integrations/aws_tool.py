from __future__ import annotations

import os

from eas.integrations.proc import run_argv
from eas.tools.models import ToolContext, ToolResult


def aws_caller_identity(ctx: ToolContext) -> ToolResult:
    env = None
    if ctx.config and ctx.config.integrations and ctx.config.integrations.aws_profile:
        env = os.environ.copy()
        env["AWS_PROFILE"] = ctx.config.integrations.aws_profile
    return run_argv(
        ["aws", "sts", "get-caller-identity", "--output", "json"],
        cwd=ctx.root,
        env=env,
    )
