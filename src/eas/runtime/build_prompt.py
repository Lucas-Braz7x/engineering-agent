from __future__ import annotations

from pathlib import Path

import yaml

from eas.runtime.models import AgentManifest, EASContext
from eas.runtime.roles import TOOL_ALIASES, denied_tools_for_policy, policy_for_agent
from eas.tools.registry import list_tools


def _project_yaml_dump(context: EASContext) -> str:
    paths = context.paths
    if paths.project_yaml.is_file():
        return paths.project_yaml.read_text(encoding="utf-8")
    return ""


def _section_files(title: str, files: tuple) -> str:
    if not files:
        return f"## {title}\n\n(none)\n"
    parts = [f"## {title}\n"]
    for item in files:
        parts.append(f"### `{item.relative_path}`\n\n{item.content.rstrip()}\n")
    return "\n".join(parts) + "\n"


def build_invoke_prompt(*, context: EASContext, agent: AgentManifest) -> str:
    requirement_block = (
        context.requirement_text.rstrip()
        if context.requirement_text
        else "(missing — create .ai/workspace/requirement.md)"
    )

    config_snapshot = {
        "project_name": context.config.project_name,
        "language": context.config.language_name,
        "framework": context.config.framework_name,
    }

    try:
        agent_ref = agent.definition_path.relative_to(context.root).as_posix()
    except ValueError:
        agent_ref = f"{agent.definition_path} (bundled with engineering-agent)"

    body = [
        f"# EAS invoke — agent `{agent.id}`",
        "",
        "Follow the agent contract below completely. Write the full artifact to the path",
        f"declared in the manifest: `{agent.artifact_path}` (include eas-artifact YAML at end).",
        "",
        "## Canonical host prompt",
        "",
        f"You are running the EAS agent \"{agent.id}\". Follow every instruction in "
        f"{agent_ref}.",
        "",
        "## Requirement",
        "",
        requirement_block,
        "",
        "## Parsed project config (summary)",
        "",
        "```yaml",
        yaml.safe_dump(config_snapshot, sort_keys=False).rstrip(),
        "```",
        "",
        _section_files("Rules (.ai/rules)", context.rules),
        _section_files("Skills (.ai/skills)", context.skills),
        _section_files(
            "Project memories (.eas — active only, curated)",
            context.memories,
        ),
        "## project.yaml (raw)",
        "",
        "```yaml",
        _project_yaml_dump(context).rstrip(),
        "```",
        "",
        "## Agent definition (full)",
        "",
        agent.definition_text.rstrip(),
        "",
        "## Role boundaries (code-enforced)",
        "",
        "Behavior is not prompt-only: the CLI blocks tools outside this agent's policy.",
        f"- **Role:** `{agent.role_id}`",
        f"- **Review peer:** `{agent.review_peer or 'none'}`",
        f"- **Artifact path:** `{agent.artifact_path}`",
        "",
        "**Allowed tools:**",
        "",
        "\n".join(f"- `{name}`" for name in sorted(agent.allowed_tools)),
        "",
        "**Denied (examples):**",
        "",
        "\n".join(
            f"- `{name}`"
            for name in sorted(denied_tools_for_policy(policy_for_agent(agent.id)))[:12]
        ),
        "(see full catalog below)",
        "",
        "Aliases blocked when the underlying tool is denied:",
        "",
        "\n".join(f"- `{alias}` → `{target}`" for alias, target in TOOL_ALIASES.items()),
        "",
        "Use tools with `--agent` so policy is enforced, e.g.",
        "",
        "```bash",
        f"engineering-agent tools read-file README.md --agent {agent.id}",
        f"engineering-agent tools write-artifact --agent {agent.id} --content '...'",
        "```",
        "",
        "## Tools catalog (all registered)",
        "",
        "\n".join(f"- `{name}` — {desc}" for name, desc in list_tools()),
        "",
    ]
    return "\n".join(body) + "\n"
