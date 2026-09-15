from __future__ import annotations

import re

import yaml

from eas.runtime.models import AgentManifest


_ARTIFACT_FENCE = re.compile(
    r"```yaml\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _parse_artifact_yaml(text: str) -> dict | None:
    matches = list(_ARTIFACT_FENCE.finditer(text))
    if not matches:
        return None
    block = matches[-1].group(1)
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def validate_artifact(
    text: str,
    agent: AgentManifest,
    *,
    check_sections: bool = False,
) -> list[str]:
    """Return human-readable validation errors (empty if ok)."""
    errors: list[str] = []

    data = _parse_artifact_yaml(text)
    if data is None:
        errors.append("Missing or invalid eas-artifact YAML fence at end of document")
        return errors

    if str(data.get("agent", "")) != agent.id:
        errors.append(
            f"eas-artifact agent must be {agent.id!r}, got {data.get('agent')!r}"
        )

    for key in agent.required_yaml_keys:
        if key not in data:
            errors.append(f"eas-artifact YAML missing required key: {key!r}")

    if check_sections and agent.required_sections:
        headings = {m.group(1).strip() for m in _SECTION.finditer(text)}
        for section in agent.required_sections:
            if section not in headings:
                errors.append(f"Missing required H2 section: ## {section}")

    return errors
