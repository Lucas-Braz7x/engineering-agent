from __future__ import annotations

import re
from pathlib import Path

from eas.detection.models import DetectionResult


def detect_go(root: Path, go_mod: Path) -> DetectionResult | None:
    try:
        text = go_mod.read_text(encoding="utf-8")
    except OSError:
        return None

    version_match = re.search(r"^go\s+(\d+\.\d+)", text, re.MULTILINE)
    go_version = version_match.group(1) if version_match else None

    framework = None
    lower = text.lower()
    if "gin-gonic/gin" in lower or "github.com/gin-gonic/gin" in lower:
        framework = "gin"
    elif "labstack/echo" in lower:
        framework = "echo"
    elif "go-chi/chi" in lower:
        framework = "chi"

    signals = ["Go"]
    if go_version:
        signals.append(f"Go {go_version}")
    if framework:
        signals.append(framework)
    signals.append("go test")

    return DetectionResult(
        project_name=root.name,
        language_name="go",
        language_version=go_version,
        framework_name=framework,
        package_manager_name="go modules",
        testing_command="go test ./...",
        build_command="go build ./...",
        signals=signals,
    )
