from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from eas.tools.models import ToolResult
from eas.tools.shell import MAX_OUTPUT_BYTES, DEFAULT_TIMEOUT_SEC

ALLOWED_BINARIES = frozenset({"gh", "docker", "aws"})


def which_or_error(binary: str) -> str | None:
    path = shutil.which(binary)
    return path


def run_argv(
    argv: list[str],
    *,
    cwd: Path,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
    env: dict[str, str] | None = None,
) -> ToolResult:
    if not argv:
        return ToolResult(ok=False, output="", error="Empty argv")
    if argv[0] not in ALLOWED_BINARIES:
        return ToolResult(ok=False, output="", error=f"Binary not allowed: {argv[0]}")
    if which_or_error(argv[0]) is None:
        return ToolResult(ok=False, output="", error=f"{argv[0]} CLI not found in PATH")

    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            shell=False,
            env=env,
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
