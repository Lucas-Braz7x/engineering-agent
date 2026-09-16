from __future__ import annotations

import re
from pathlib import Path

import yaml

from eas.bundled_paths import bundled_root
from eas.runtime.models import AgentManifest
from eas.runtime.roles import merge_allowed_tools, policy_for_agent


class AgentLoadError(Exception):
    pass


_ALLOWED_AGENTS = frozenset(
    {"architect", "tester", "reviewer", "debugger", "fixer", "documenter"}
)


def _candidate_agent_paths(root: Path, agent_id: str) -> tuple[Path, ...]:
    return (
        root / ".ai" / "agents" / f"{agent_id}.md",
        bundled_root() / "agents" / f"{agent_id}.md",
    )


def load_agent(root: Path, agent_id: str) -> AgentManifest:
    if agent_id not in _ALLOWED_AGENTS:
        raise AgentLoadError(
            f"Unknown agent {agent_id!r}. Allowed: {', '.join(sorted(_ALLOWED_AGENTS))}"
        )

    path: Path | None = None
    for candidate in _candidate_agent_paths(root, agent_id):
        if candidate.is_file():
            path = candidate
            break

    if path is None:
        repo_path = root / ".ai" / "agents" / f"{agent_id}.md"
        bundled_path = bundled_root() / "agents" / f"{agent_id}.md"
        raise AgentLoadError(
            f"Missing agent definition: {repo_path}\n"
            f"  (bundled fallback also missing: {bundled_path})"
        )

    text = path.read_text(encoding="utf-8")
    match = re.search(r"```yaml\s*\n(.*?)```", text, re.DOTALL)
    if not match:
        raise AgentLoadError(f"No YAML manifest block in {path}")

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise AgentLoadError(f"Invalid agent manifest YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise AgentLoadError(f"Agent manifest must be a mapping in {path}")

    for key in ("id", "artifact_path"):
        if not data.get(key):
            raise AgentLoadError(f"Agent manifest missing {key!r} in {path}")

    agent_id = str(data["id"])
    try:
        role_policy = policy_for_agent(agent_id)
    except KeyError as exc:
        raise AgentLoadError(str(exc)) from exc

    manifest_tools = data.get("allowed_tools")
    if manifest_tools is not None and not isinstance(manifest_tools, list):
        raise AgentLoadError(f"allowed_tools must be a list in {path}")
    try:
        allowed = merge_allowed_tools(
            agent_id,
            manifest_tools if manifest_tools else None,
        )
    except ValueError as exc:
        raise AgentLoadError(str(exc)) from exc

    review_peer = data.get("review_peer", role_policy.review_peer)
    if review_peer is not None:
        review_peer = str(review_peer)

    return AgentManifest(
        id=agent_id,
        version=str(data.get("version", "0.0.0")),
        artifact_path=str(data["artifact_path"]),
        definition_path=path,
        definition_text=text,
        role_id=str(data.get("role", role_policy.role_id)),
        allowed_tools=allowed,
        review_peer=review_peer,
        required_sections=role_policy.required_sections,
        required_yaml_keys=role_policy.required_yaml_keys,
    )
