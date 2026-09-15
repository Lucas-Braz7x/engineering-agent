from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from eas.context.paths import WorkspacePaths

_MAX_SNIPPET = 400

# requirement.md — títulos em PT ou EN
_HEADING_ALIASES: dict[str, tuple[str, ...]] = {
    "titulo": ("Title", "Título", "Titulo"),
    "problema": ("Problem", "Problema"),
    "usuario": ("User story", "História de usuário", "Historia de usuario"),
    "resumo": ("Summary", "Resumo"),
    "escopo": ("Scope", "Escopo"),
}


@dataclass(frozen=True)
class PurposeField:
    """Um aspecto do propósito, com rótulo e fonte em pt-BR."""

    label: str
    text: str
    source: str


@dataclass(frozen=True)
class ProjectPurpose:
    fields: tuple[PurposeField, ...]

    def is_empty(self) -> bool:
        return not self.fields


def _trim(text: str, limit: int = _MAX_SNIPPET) -> str:
    one_line = " ".join(text.split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1].rstrip() + "…"


def _markdown_section_any(text: str, headings: tuple[str, ...]) -> str | None:
    for heading in headings:
        pattern = re.compile(
            rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            continue
        body = match.group(1).strip()
        if not body:
            continue
        para = body.split("\n\n")[0].strip()
        if para:
            return para
    return None


def _readme_intro(path: Path) -> PurposeField | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    lines = stripped.splitlines()
    body_lines: list[str] = []
    passed_title = False
    for line in lines:
        if line.startswith("# ") and not passed_title:
            passed_title = True
            continue
        if line.startswith("#"):
            if body_lines:
                break
            continue
        if not passed_title:
            continue
        if not line.strip():
            if body_lines:
                break
            continue
        body_lines.append(line.strip())
    if not body_lines:
        return None
    blurb = _trim(" ".join(body_lines))
    if len(blurb) < 20:
        return None
    return PurposeField(label="Resumo", text=blurb, source="README.md")


def _requirement_fields(text: str) -> list[PurposeField]:
    fields: list[PurposeField] = []
    mapping = (
        ("O que entrega", "titulo"),
        ("Problema que resolve", "problema"),
        ("Para quem", "usuario"),
        ("Resumo do requisito", "resumo"),
        ("Escopo declarado", "escopo"),
    )
    for label, key in mapping:
        section = _markdown_section_any(text, _HEADING_ALIASES[key])
        if section:
            fields.append(
                PurposeField(
                    label=label,
                    text=_trim(section),
                    source=f"requirement.md ({_HEADING_ALIASES[key][0]})",
                )
            )
    return fields


def _pyproject_description(root: Path) -> PurposeField | None:
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    desc = project.get("description")
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        return None
    return PurposeField(
        label="Resumo",
        text=_trim(desc.strip()),
        source="pyproject.toml (descrição)",
    )


def _package_json_description(root: Path) -> PurposeField | None:
    path = root / "package.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    desc = data.get("description")
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        return None
    return PurposeField(
        label="Resumo",
        text=_trim(desc.strip()),
        source="package.json (descrição)",
    )


def _project_yaml_description(paths: WorkspacePaths) -> PurposeField | None:
    if not paths.project_yaml.is_file():
        return None
    try:
        data = yaml.safe_load(paths.project_yaml.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    desc = project.get("description")
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        return None
    return PurposeField(
        label="Resumo",
        text=_trim(desc.strip()),
        source="project.yaml (project.description)",
    )


def _merge_fields(fields: list[PurposeField]) -> tuple[PurposeField, ...]:
    """Remove textos duplicados; mantém o primeiro por label+texto."""
    seen_text: set[str] = set()
    out: list[PurposeField] = []
    for field in fields:
        key = field.text.casefold()
        if key in seen_text:
            continue
        seen_text.add(key)
        out.append(field)
    return tuple(out)


def gather_project_purpose(
    root: Path,
    paths: WorkspacePaths,
    requirement_text: str | None,
) -> ProjectPurpose:
    """Monta propósito do projeto a partir de fontes humanas (sem LLM)."""
    ordered: list[PurposeField] = []

    for getter in (
        lambda: _project_yaml_description(paths),
        lambda: _pyproject_description(root),
        lambda: _package_json_description(root),
        lambda: _readme_intro(root / "README.md"),
    ):
        field = getter()
        if field:
            ordered.append(field)

    if requirement_text:
        ordered.extend(_requirement_fields(requirement_text))

    return ProjectPurpose(fields=_merge_fields(ordered))


def format_purpose_block(purpose: ProjectPurpose) -> str:
    if purpose.is_empty():
        return (
            "Propósito:\n"
            "- (não identificado — preencha README, requirement.md § Problema, "
            "ou project.description em project.yaml)"
        )
    lines = ["Propósito:"]
    for field in purpose.fields:
        lines.append(f"- {field.label}: {field.text}")
        lines.append(f"  Fonte: {field.source}")
    return "\n".join(lines)


def requirement_title(text: str) -> str | None:
    """Título do requisito (seções Title / Título)."""
    section = _markdown_section_any(text, _HEADING_ALIASES["titulo"])
    if section:
        return _trim(section, limit=120)
    return None
