from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from eas.tools.models import ToolContext, ToolResult

DEFAULT_TIMEOUT_SEC = 120
MAX_OUTPUT_BYTES = 256_000

_BLOCKED_TOKENS = frozenset(
    {
        "rm",
        "sudo",
        "chmod",
        "chown",
        "mkfs",
        "dd",
        "shutdown",
        "reboot",
    }
)


def _check_command(argv: list[str]) -> str | None:
    if not argv:
        return "Empty command"
    if argv[0] in _BLOCKED_TOKENS:
        return f"Command not allowed: {argv[0]}"
    return None


def run_command(
    ctx: ToolContext,
    *,
    command: str,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> ToolResult:
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    blocked = _check_command(argv)
    if blocked:
        return ToolResult(ok=False, output="", error=blocked)

    try:
        completed = subprocess.run(
            argv,
            cwd=ctx.root,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            ok=False,
            output="",
            error=f"Command timed out after {timeout_sec}s",
            exit_code=-1,
        )
    except OSError as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    combined = stdout
    if stderr:
        combined = f"{stdout}\n--- stderr ---\n{stderr}".strip()

    if len(combined.encode("utf-8")) > MAX_OUTPUT_BYTES:
        combined = combined[:MAX_OUTPUT_BYTES] + "\n... (truncated)"

    ok = completed.returncode == 0
    return ToolResult(
        ok=ok,
        output=combined,
        error=None if ok else f"exit code {completed.returncode}",
        exit_code=completed.returncode,
    )
