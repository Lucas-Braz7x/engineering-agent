from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRolePolicy:
    """Code-enforced boundaries for an EAS agent (not prompt-only)."""

    role_id: str
    summary: str
    allowed_tools: frozenset[str]
    review_peer: str | None
    required_sections: tuple[str, ...]
    required_yaml_keys: tuple[str, ...]


# Logical aliases documented for hosts — blocked at tool layer via allowed_tools.
TOOL_ALIASES: dict[str, str] = {
    "edit_source": "write_file",
    "run_git_commit": "run_command",
}

# Future implementer profile (no bundled agent.md yet).
CODER_ROLE = AgentRolePolicy(
    role_id="coder",
    summary="Implement production code; no architecture artifacts",
    allowed_tools=frozenset(
        {
            "read_file",
            "write_file",
            "search_code",
            "run_tests",
            "git_diff",
            "git_status",
            "git_log",
        }
    ),
    review_peer="reviewer",
    required_sections=(),
    required_yaml_keys=(),
)

AGENT_ROLE_POLICIES: dict[str, AgentRolePolicy] = {
    "architect": AgentRolePolicy(
        role_id="architect",
        summary="Design and artifacts only — no source edits or shell",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_artifact",
                "git_status",
                "git_log",
            }
        ),
        review_peer="reviewer",
        required_sections=(
            "Summary",
            "Requirements",
            "Current state",
            "Proposed design",
            "Implementation plan",
        ),
        required_yaml_keys=("agent", "status", "risk_level"),
    ),
    "reviewer": AgentRolePolicy(
        role_id="reviewer",
        summary="Read diff and repo; write review artifact only",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_artifact",
                "git_diff",
                "git_status",
                "git_log",
                "run_tests",
                "github_pr_view",
                "ci_github_runs",
            }
        ),
        review_peer="architect",
        required_sections=("Review summary", "Scope reviewed", "Findings"),
        required_yaml_keys=("agent", "status"),
    ),
    "tester": AgentRolePolicy(
        role_id="tester",
        summary="Test strategy from diff and architecture",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_artifact",
                "git_diff",
                "git_status",
                "run_tests",
            }
        ),
        review_peer="reviewer",
        required_sections=("Summary", "Proposed test cases"),
        required_yaml_keys=("agent", "status"),
    ),
    "debugger": AgentRolePolicy(
        role_id="debugger",
        summary="Structured investigation before fixes",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_artifact",
                "git_diff",
                "git_status",
                "run_tests",
                "run_command",
            }
        ),
        review_peer="fixer",
        required_sections=("Summary", "Root cause"),
        required_yaml_keys=("agent", "status", "root_cause_confidence"),
    ),
    "fixer": AgentRolePolicy(
        role_id="fixer",
        summary="Minimal fix plan — no automatic patches",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_artifact",
                "git_diff",
                "git_status",
                "run_tests",
            }
        ),
        review_peer="reviewer",
        required_sections=("Summary", "Proposed changes", "Verification"),
        required_yaml_keys=("agent", "status"),
    ),
    "documenter": AgentRolePolicy(
        role_id="documenter",
        summary="Product docs and ADRs — no source or CI edits",
        allowed_tools=frozenset(
            {
                "read_file",
                "search_code",
                "write_file",
                "write_artifact",
                "git_diff",
                "git_status",
                "git_log",
            }
        ),
        review_peer="reviewer",
        required_sections=(
            "Summary",
            "Scope and inputs used",
            "Documentation changes",
            "ADRs",
        ),
        required_yaml_keys=("agent", "status"),
    ),
}


def policy_for_agent(agent_id: str) -> AgentRolePolicy:
    try:
        return AGENT_ROLE_POLICIES[agent_id]
    except KeyError as exc:
        raise KeyError(f"No role policy for agent {agent_id!r}") from exc


def merge_allowed_tools(
    agent_id: str,
    manifest_override: list[str] | tuple[str, ...] | None,
) -> frozenset[str]:
    base = policy_for_agent(agent_id).allowed_tools
    if not manifest_override:
        return base
    unknown = set(manifest_override) - base
    if unknown:
        raise ValueError(
            f"Manifest allowed_tools not subset of role policy for {agent_id!r}: "
            f"{sorted(unknown)}"
        )
    return frozenset(manifest_override)


def denied_tools_for_policy(policy: AgentRolePolicy) -> frozenset[str]:
    from eas.tools.registry import TOOL_CATALOG

    return frozenset(TOOL_CATALOG) - policy.allowed_tools
