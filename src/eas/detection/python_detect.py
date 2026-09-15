from __future__ import annotations

import re
import tomllib
from pathlib import Path

from eas.detection.models import DetectionResult


def _requires_python_version(spec: str) -> str | None:
    match = re.search(r"(\d+\.\d+)", spec)
    return match.group(1) if match else None


def _dep_names(deps: list) -> set[str]:
    names: set[str] = set()
    for item in deps:
        text = str(item).lower()
        name = re.split(r"[<>=!~\[]", text, maxsplit=1)[0].strip()
        if name:
            names.add(name)
    return names


def _framework_from_deps(names: set[str]) -> str | None:
    if "fastapi" in names:
        return "fastapi"
    if "django" in names:
        return "django"
    if "flask" in names:
        return "flask"
    if "typer" in names:
        return "typer"
    return None


def _package_manager(root: Path) -> str:
    if (root / "uv.lock").is_file():
        return "uv"
    if (root / "poetry.lock").is_file():
        return "poetry"
    if (root / "Pipfile").is_file():
        return "pipenv"
    return "pip"


def detect_python(root: Path, pyproject: Path) -> DetectionResult | None:
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None

    project = data.get("project") or {}
    if not isinstance(project, dict):
        project = {}

    name = project.get("name") or root.name
    requires = project.get("requires-python")
    version = _requires_python_version(str(requires)) if requires else None

    deps = project.get("dependencies") or []
    optional = project.get("optional-dependencies") or {}
    all_names = _dep_names(deps if isinstance(deps, list) else [])
    if isinstance(optional, dict):
        for group in optional.values():
            if isinstance(group, list):
                all_names |= _dep_names(group)

    pm = _package_manager(root)
    framework = _framework_from_deps(all_names)

    testing_command = "pytest"
    if pm == "uv":
        testing_command = "uv run pytest"

    build_command = 'pip install -e ".[dev]"'
    if pm == "uv":
        build_command = "uv sync --dev"

    signals = ["Python"]
    if version:
        signals.append(f"Python {version}")
    if framework:
        signals.append(framework)
    signals.append(pm)
    tool = data.get("tool")
    has_pytest_config = isinstance(tool, dict) and "pytest" in tool
    if "pytest" in all_names or has_pytest_config:
        signals.append("pytest")

    return DetectionResult(
        project_name=str(name),
        language_name="python",
        language_version=version,
        framework_name=framework,
        package_manager_name=pm,
        testing_command=testing_command,
        build_command=build_command,
        signals=signals,
    )
