from __future__ import annotations

import json
from pathlib import Path

from eas.detection.models import DetectionResult


def _package_manager(root: Path, package_json: dict) -> str:
    pm_field = package_json.get("packageManager") or ""
    if pm_field.startswith("pnpm"):
        return "pnpm"
    if pm_field.startswith("yarn"):
        return "yarn"
    if pm_field.startswith("npm"):
        return "npm"
    if (root / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (root / "yarn.lock").is_file():
        return "yarn"
    return "npm"


def _all_dependency_names(package_json: dict) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        block = package_json.get(key) or {}
        if isinstance(block, dict):
            names.update(block.keys())
    return names


def _framework_from_deps(names: set[str]) -> str | None:
    if "@nestjs/core" in names:
        return "nestjs"
    if "next" in names:
        return "next"
    if "express" in names:
        return "express"
    if "react" in names or "react-dom" in names:
        return "react"
    return None


def _run_prefix(pm: str) -> str:
    return {"pnpm": "pnpm", "yarn": "yarn", "npm": "npm"}.get(pm, "npm")


def detect_node(root: Path, package_json_path: Path) -> DetectionResult | None:
    try:
        package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(package_json, dict):
        return None

    name = package_json.get("name") or root.name
    deps = _all_dependency_names(package_json)
    pm = _package_manager(root, package_json)
    prefix = _run_prefix(pm)

    language = "javascript"
    signals_lang = "JavaScript"
    if "typescript" in deps or (root / "tsconfig.json").is_file():
        language = "typescript"
        signals_lang = "TypeScript"

    framework = _framework_from_deps(deps)
    scripts = package_json.get("scripts") or {}
    testing_command = None
    if isinstance(scripts, dict) and scripts.get("test"):
        testing_command = f"{prefix} test"
    build_command = None
    if isinstance(scripts, dict) and scripts.get("build"):
        build_command = f"{prefix} run build"

    engines = package_json.get("engines") or {}
    node_version = None
    if isinstance(engines, dict) and engines.get("node"):
        node_version = str(engines["node"]).lstrip("v^>= ")

    signals = [signals_lang]
    if node_version:
        signals.append(f"Node.js {node_version}")
    elif (root / "package.json").is_file():
        signals.append("Node.js")
    signals.append(pm)
    if framework:
        signals.append(framework)
    for test_runner in ("jest", "vitest", "mocha"):
        if test_runner in deps:
            signals.append(test_runner)
            break

    return DetectionResult(
        project_name=str(name),
        language_name=language,
        language_version=node_version,
        framework_name=framework,
        package_manager_name=pm,
        testing_command=testing_command,
        build_command=build_command,
        signals=signals,
    )
