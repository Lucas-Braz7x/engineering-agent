from __future__ import annotations

from pathlib import Path


def architecture_approved(root: Path) -> bool:
    path = root / ".ai" / "workspace" / "approval.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return "decision: approved" in text or "decision: approved_with_notes" in text


def approval_hint() -> str:
    return (
        "Architecture approval required before tester/reviewer.\n"
        "Create .ai/workspace/approval.md with decision: approved\n"
        "or pass --assume-approved (you confirm architecture was reviewed)."
    )
