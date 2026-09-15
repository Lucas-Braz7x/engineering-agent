from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError

from eas.context.integrations_config import IntegrationsConfig, parse_integrations
from eas.context.limits import LoopLimits, parse_limits


class ProjectConfigError(Exception):
    """Failed to load or parse project configuration."""


@dataclass(frozen=True)
class ProjectConfig:
    project_name: str | None = None
    language_name: str | None = None
    language_version: str | None = None
    framework_name: str | None = None
    package_manager_name: str | None = None
    database_name: str | None = None
    testing_command: str | None = None
    build_command: str | None = None
    limits: LoopLimits | None = None
    integrations: IntegrationsConfig | None = None


def _nested_str(data: dict[str, Any], *keys: str) -> str | None:
    node: Any = data
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return str(node) if node is not None else None


def _parse_config(data: Any) -> ProjectConfig:
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ProjectConfigError("project.yaml root must be a mapping")

    return ProjectConfig(
        project_name=_nested_str(data, "project", "name"),
        language_name=_nested_str(data, "language", "name"),
        language_version=_nested_str(data, "language", "version"),
        framework_name=_nested_str(data, "framework", "name"),
        package_manager_name=_nested_str(data, "package_manager", "name"),
        database_name=_nested_str(data, "database", "name"),
        testing_command=_nested_str(data, "testing", "command"),
        build_command=_nested_str(data, "build", "command"),
        limits=parse_limits(data),
        integrations=parse_integrations(data),
    )


def load_project_config(path: Path) -> ProjectConfig:
    if not path.is_file():
        raise ProjectConfigError(f"Missing project config: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProjectConfigError(f"Cannot read {path}: {exc}") from exc

    try:
        data = yaml.safe_load(raw)
    except YAMLError as exc:
        raise ProjectConfigError(f"Invalid YAML in {path}: {exc}") from exc

    return _parse_config(data)
