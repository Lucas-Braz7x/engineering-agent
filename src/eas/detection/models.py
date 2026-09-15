from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DetectionResult:
    """Stack detected from repository manifests."""

    project_name: str
    language_name: str | None = None
    language_version: str | None = None
    framework_name: str | None = None
    package_manager_name: str | None = None
    database_name: str | None = None
    testing_command: str | None = None
    build_command: str | None = None
    signals: list[str] = field(default_factory=list)
    manifests: list[str] = field(default_factory=list)
    monorepo: bool = False
