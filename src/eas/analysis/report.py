from __future__ import annotations

from pathlib import Path

from eas.analysis.purpose import (
    ProjectPurpose,
    format_purpose_block,
    gather_project_purpose,
    requirement_title,
)
from eas.context.loader import ProjectConfig
from eas.context.paths import WorkspacePaths


def _requirement_title(requirement_md: Path) -> str | None:
    if not requirement_md.is_file():
        return None
    text = requirement_md.read_text(encoding="utf-8")
    return requirement_title(text)


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
    purpose: ProjectPurpose | None = None,
) -> str:
    title = _requirement_title(paths.requirement_md)
    project_label = config.project_name or "(sem nome)"
    if title:
        project_label = f"{project_label} — {title}"

    stack_lines = [
        line
        for line in (
            _stack_line(
                "linguagem",
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
            _stack_line("gerenciador de pacotes", config.package_manager_name),
            _stack_line("banco de dados", config.database_name),
            _stack_line("testes", config.testing_command),
            _stack_line("build", config.build_command),
        )
        if line
    ]
    if not stack_lines:
        stack_lines = ["- (nenhum campo de stack em project.yaml)"]

    stack_block = "Stack técnica:\n" + "\n".join(stack_lines)
    workspace_block = "Workspace EAS:\n" + "\n".join(
        (
            f"- requisito: {_display_path(paths.root, paths.requirement_md)}",
            f"- arquitetura: {_display_path(paths.root, paths.architecture_md)}",
        )
    )
    recommendation_block = "Próximos passos:\n" + "\n".join(
        (
            "- engineering-agent analyze --agent architect --prepare",
            "- ou: analyze --agent architect --invoke (ANTHROPIC_API_KEY + pip install '.[llm]')",
            "- host manual: .ai/hosts/prompts.md",
        )
    )
    req_label = "presente" if has_requirement else "ausente"
    context_block = "Contexto carregado:\n" + "\n".join(
        (
            f"- regras: {rules_count} arquivo(s)",
            f"- skills: {skills_count} arquivo(s)",
            f"- requirement.md: {req_label}",
        )
    )

    if purpose is None:
        purpose = gather_project_purpose(paths.root, paths, None)
    purpose_block = format_purpose_block(purpose)

    sections = [
        f"Análise EAS v{version}",
        f"Projeto: {project_label}",
        purpose_block,
        stack_block,
        context_block,
        workspace_block,
        recommendation_block,
        f"Rascunho de arquitetura: {draft_status}",
    ]
    return "\n\n".join(sections) + "\n"
