from __future__ import annotations

from eas.tools.models import ToolContext, ToolResult
from eas.tools.shell import run_command


def run_tests(ctx: ToolContext) -> ToolResult:
    if ctx.config is None or not ctx.config.testing_command:
        return ToolResult(
            ok=False,
            output="",
            error="No testing.command in .ai/project.yaml — set it or use tools run",
        )
    return run_command(ctx, command=ctx.config.testing_command)
