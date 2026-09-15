from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eas.context.loader import ProjectConfig


@dataclass(frozen=True)
class ToolContext:
    root: Path
    config: ProjectConfig | None = None


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    output: str
    error: str | None = None
    exit_code: int | None = None
