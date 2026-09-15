from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from eas.detection.models import DetectionResult


def detection_to_mapping(result: DetectionResult) -> dict[str, Any]:
    data: dict[str, Any] = {
        "project": {"name": result.project_name},
    }
    if result.language_name:
        lang: dict[str, str] = {"name": result.language_name}
        if result.language_version:
            lang["version"] = result.language_version
        data["language"] = lang
    if result.framework_name:
        data["framework"] = {"name": result.framework_name}
    if result.package_manager_name:
        data["package_manager"] = {"name": result.package_manager_name}
    if result.database_name:
        data["database"] = {"name": result.database_name}
    if result.testing_command:
        data["testing"] = {"command": result.testing_command}
    if result.build_command:
        data["build"] = {"command": result.build_command}
    if result.manifests:
        detection: dict[str, Any] = {"manifests": result.manifests}
        if result.monorepo:
            detection["monorepo"] = True
        data["detection"] = detection
    return data


def write_project_yaml(path: Path, result: DetectionResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = detection_to_mapping(result)
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")
