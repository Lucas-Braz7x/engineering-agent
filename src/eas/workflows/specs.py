from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    description: str
    steps: tuple[str, ...]
    requires_approval_before: frozenset[str] = frozenset()


# Aligned with .ai/workflows/feature.md (Phase 0 scope: no Coder/Challenger in CLI).
WORKFLOW_FEATURE = WorkflowSpec(
    id="feature",
    description="Requirement → architect → (approval) → tester → reviewer → documenter",
    steps=("architect", "tester", "reviewer", "documenter"),
    requires_approval_before=frozenset({"tester", "reviewer"}),
)

WORKFLOW_REVIEW = WorkflowSpec(
    id="review",
    description="Git context → reviewer → documenter",
    steps=("reviewer", "documenter"),
)

WORKFLOW_BUG = WorkflowSpec(
    id="bug",
    description="Bug report → debugger → (fix manual) → tester → reviewer → documenter",
    steps=("debugger", "tester", "reviewer", "documenter"),
    requires_approval_before=frozenset({"tester", "reviewer"}),
)

WORKFLOWS: dict[str, WorkflowSpec] = {
    "feature": WORKFLOW_FEATURE,
    "review": WORKFLOW_REVIEW,
    "bug": WORKFLOW_BUG,
}
