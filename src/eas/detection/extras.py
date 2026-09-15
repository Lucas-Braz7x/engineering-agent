from __future__ import annotations

import re
from pathlib import Path

from eas.detection.models import DetectionResult


def _database_from_compose(root: Path) -> str | None:
    compose_names = ("docker-compose.yml", "docker-compose.yaml", "compose.yml")
    for name in compose_names:
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        if "postgres" in text:
            return "postgresql"
        if "mysql" in text or "mariadb" in text:
            return "mysql"
        if "mongo" in text:
            return "mongodb"
    return None


def enrich_signals(root: Path, result: DetectionResult) -> DetectionResult:
    signals = list(dict.fromkeys(result.signals))

    if (root / ".git").exists():
        signals.append("Git")

    if (root / "Dockerfile").is_file() or any(
        (root / n).is_file() for n in ("docker-compose.yml", "docker-compose.yaml")
    ):
        signals.append("Docker")

    database = result.database_name or _database_from_compose(root)
    if database:
        db_labels = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
        }
        signals.append(db_labels.get(database, database.title()))

    return DetectionResult(
        project_name=result.project_name,
        language_name=result.language_name,
        language_version=result.language_version,
        framework_name=result.framework_name,
        package_manager_name=result.package_manager_name,
        database_name=database,
        testing_command=result.testing_command,
        build_command=result.build_command,
        signals=signals,
        manifests=result.manifests,
        monorepo=result.monorepo,
    )
