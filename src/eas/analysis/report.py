from __future__ import annotations

import re
from pathlib import Path

from eas.context.loader import ProjectConfig
from eas.context.paths import WorkspacePaths


def _requirement_title(requirement_md: Path) -> str | None:
    if not requirement_md.is_file():
        return None
    text = requirement_md.read_text(encoding="utf-8")
    match = re.search(r"^## Title\s*\n\s*(.+)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _stack_line(label: str, value: str | None) -> str | None:
    if not value:
        return None
    return f"- {label}: {value}"


def build_report(
    *,
    version: str,
    config: ProjectConfig,
    paths: WorkspacePaths,
    draft_status: str,
    rules_count: int = 0,
    skills_count: int = 0,
    has_requirement: bool = False,
) -> str:
    title = _requirement_title(paths.requirement_md)
    project_label = config.project_name or "(unknown)"
    if title:
        project_label = f"{project_label} — {title}"

    stack_lines = [
        line
        for line in (
            _stack_line(
                "language",
                " ".join(
                    part
                    for part in (
                        config.language_name,
                        config.language_version,
                    )
                    if part
                )
                or None,
            ),
            _stack_line("framework", config.framework_name),
            _stack_line("package_manager", config.package_manager_name),
            _stack_line("database", config.database_name),
            _stack_line("testing", config.testing_command),
            _stack_line("build", config.build_command),
        )
        if line
    ]
    if not stack_lines:
        stack_lines = ["- (no stack fields in project.yaml)"]

    stack_block = "Stack:\n" + "\n".join(stack_lines)
    workspace_block = "Workspace:\n" + "\n".join(
        (
            f"- requirement: {_display_path(paths.root, paths.requirement_md)}",
            f"- architecture: {_display_path(paths.root, paths.architecture_md)}",
        )
    )
    recommendation_block = "Recommendation:\n" + "\n".join(
        (
            "- Phase 2: engineering-agent analyze --agent architect --prepare",
            "- Or: analyze --agent architect --invoke (ANTHROPIC_API_KEY + pip install '.[llm]')",
            "- Manual host: .ai/hosts/prompts.md",
        )
    )
    context_block = "Context:\n" + "\n".join(
        (
            f"- rules: {rules_count} file(s)",
            f"- skills: {skills_count} file(s)",
            f"- requirement: {'present' if has_requirement else 'missing'}",
        )
    )

    sections = [
        f"EAS analyze v{version}",
        f"Project: {project_label}",
        stack_block,
        context_block,
        workspace_block,
        recommendation_block,
        f"Draft: {draft_status}",
    ]
    return "\n\n".join(sections) + "\n"
