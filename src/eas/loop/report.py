from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from eas.loop.budget import LoopBudget


@dataclass(frozen=True)
class LoopOutcome:
    status: str  # SUCCESS | WORKFLOW_BLOCKED | TESTS_FAILED
    reason: str
    budget: LoopBudget
    last_test_exit_code: int | None = None


def write_loop_report(root: Path, outcome: LoopOutcome) -> Path:
    path = root / ".ai" / "workspace" / "loop-report.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Autonomous loop report",
        "",
        f"**Status:** `{outcome.status}`",
        "",
        f"**Reason:** {outcome.reason}",
        "",
        "## Budget",
        "",
        f"- iterations: {outcome.budget.iterations} / {outcome.budget.limits.max_iterations}",
        f"- command_executions: {outcome.budget.command_executions} / "
        f"{outcome.budget.limits.max_command_execution}",
        f"- agent_calls: {outcome.budget.agent_calls} / {outcome.budget.limits.max_agent_calls}",
        "",
    ]
    if outcome.last_test_exit_code is not None:
        lines.append(f"Last test exit code: {outcome.last_test_exit_code}")
        lines.append("")

    footer = {
        "eas-artifact": "loop v0.1",
        "agent": "loop",
        "status": outcome.status.lower(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "budget": {
            "iterations": outcome.budget.iterations,
            "command_executions": outcome.budget.command_executions,
            "agent_calls": outcome.budget.agent_calls,
        },
    }
    lines.append("```yaml")
    lines.append(yaml.safe_dump(footer, sort_keys=False).rstrip())
    lines.append("```")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
