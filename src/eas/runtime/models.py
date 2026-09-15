from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eas.context.loader import ProjectConfig
from eas.context.paths import WorkspacePaths


@dataclass(frozen=True)
class ContextFile:
    relative_path: str
    content: str


@dataclass(frozen=True)
class EASContext:
    root: Path
    paths: WorkspacePaths
    config: ProjectConfig
    rules: tuple[ContextFile, ...]
    skills: tuple[ContextFile, ...]
    requirement_text: str | None


@dataclass(frozen=True)
class AgentManifest:
    id: str
    version: str
    artifact_path: str
    definition_path: Path
    definition_text: str


@dataclass(frozen=True)
class PrepareResult:
    run_id: str
    run_dir: Path
    invoke_path: Path
    artifact_path: Path


@dataclass(frozen=True)
class InvokeResult:
    run_id: str
    artifact_path: Path
    bytes_written: int
