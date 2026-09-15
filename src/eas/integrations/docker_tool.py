from __future__ import annotations

from pathlib import Path

from eas.context.integrations_config import IntegrationsConfig
from eas.integrations.proc import run_argv
from eas.tools.models import ToolContext, ToolResult


def _compose_file(ctx: ToolContext) -> Path:
    if ctx.config and ctx.config.integrations:
        name = ctx.config.integrations.docker_compose_file
    else:
        name = IntegrationsConfig().docker_compose_file
    return ctx.root / name


def docker_compose_ps(ctx: ToolContext) -> ToolResult:
    compose = _compose_file(ctx)
    if not compose.is_file():
        return ToolResult(ok=False, output="", error=f"Compose file not found: {compose.name}")
    return run_argv(
        ["docker", "compose", "-f", str(compose), "ps"],
        cwd=ctx.root,
    )


def docker_compose_config(ctx: ToolContext) -> ToolResult:
    compose = _compose_file(ctx)
    if not compose.is_file():
        return ToolResult(ok=False, output="", error=f"Compose file not found: {compose.name}")
    return run_argv(
        ["docker", "compose", "-f", str(compose), "config", "--services"],
        cwd=ctx.root,
    )
