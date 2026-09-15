from __future__ import annotations

import re
import tomllib
from pathlib import Path

from eas.detection.models import DetectionResult


def _framework_from_toml_text(text: str) -> str | None:
    lower = text.lower()
    if "axum" in lower:
        return "axum"
    if "actix-web" in lower or "actix_web" in lower:
        return "actix"
    if "rocket" in lower:
        return "rocket"
    return None


def detect_rust(root: Path, cargo_toml: Path) -> DetectionResult | None:
    try:
        text = cargo_toml.read_text(encoding="utf-8")
        data = tomllib.loads(text)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    package = data.get("package") or {}
    if not isinstance(package, dict):
        package = {}

    name = package.get("name") or root.name
    rust_version = package.get("rust-version")
    if rust_version:
        rust_version = str(rust_version).lstrip(">=^ ")
    else:
        match = re.search(r"rust-version\s*=\s*[\"']([^\"']+)", text)
        rust_version = match.group(1) if match else None

    framework = _framework_from_toml_text(text)
    signals = ["Rust"]
    if rust_version:
        signals.append(f"Rust {rust_version}")
    if framework:
        signals.append(framework)
    signals.append("cargo test")

    return DetectionResult(
        project_name=str(name),
        language_name="rust",
        language_version=rust_version,
        framework_name=framework,
        package_manager_name="cargo",
        testing_command="cargo test",
        build_command="cargo build",
        signals=signals,
    )
