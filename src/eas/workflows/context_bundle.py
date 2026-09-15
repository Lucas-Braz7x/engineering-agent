from __future__ import annotations

from pathlib import Path

from eas.context.loader import ProjectConfig
from eas.tools.models import ToolContext
from eas.tools.registry import execute


def gather_git_context(
    root: Path,
    config: ProjectConfig | None,
    *,
    git_base: str | None,
    git_head: str | None,
    include_tests: bool,
) -> list[tuple[str, str]]:
    ctx = ToolContext(root=root, config=config)
    sections: list[tuple[str, str]] = []

    diff = execute(ctx, "git_diff", base=git_base, head=git_head)
    diff_body = diff.output if diff.ok else (diff.error or "git diff failed")
    sections.append(("Git diff", diff_body))

    status = execute(ctx, "git_status")
    if status.output:
        sections.append(("Git status", status.output))

    arch = root / ".ai" / "workspace" / "architecture.md"
    if arch.is_file():
        sections.append(("architecture.md (existing)", arch.read_text(encoding="utf-8")))

    test_plan = root / ".ai" / "workspace" / "test-plan.md"
    if test_plan.is_file():
        sections.append(("test-plan.md (existing)", test_plan.read_text(encoding="utf-8")))

    debug_report = root / ".ai" / "workspace" / "debug-report.md"
    if debug_report.is_file():
        sections.append(("debug-report.md (existing)", debug_report.read_text(encoding="utf-8")))

    if include_tests:
        tests = execute(ctx, "run_tests")
        label = "Test run output" if tests.ok else "Test run (failed)"
        body = tests.output or tests.error or ""
        sections.append((label, body))

    return sections


def read_bug_report(root: Path) -> str | None:
    path = root / ".ai" / "workspace" / "bug-report.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def write_bug_report(root: Path, description: str) -> Path:
    path = root / ".ai" / "workspace" / "bug-report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Bug report\n\n{description.strip()}\n",
        encoding="utf-8",
    )
    return path
