from __future__ import annotations

from pathlib import Path

from eas.bundled_paths import bundled_root
from eas.context.loader import ProjectConfig, load_project_config
from eas.context.paths import workspace_paths
from eas.runtime.models import ContextFile, EASContext
from eas.store.connection import open_store_optional
from eas.store.memory_service import active_memories_for_context
from eas.store.repository import ensure_project


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _collect_markdown_files(directory: Path, base: Path) -> tuple[ContextFile, ...]:
    if not directory.is_dir():
        return ()
    files: list[ContextFile] = []
    for path in sorted(directory.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        files.append(ContextFile(relative_path=rel, content=_read_text(path)))
    return tuple(files)


def load_eas_context(root: Path, *, config: ProjectConfig | None = None) -> EASContext:
    paths = workspace_paths(root)
    if config is None:
        config = load_project_config(paths.project_yaml)

    ai_dir = root / ".ai"
    rules = _collect_markdown_files(ai_dir / "rules", ai_dir)
    if not rules:
        bundled = bundled_root()
        rules = _collect_markdown_files(bundled / "rules", bundled)

    skills = _collect_markdown_files(ai_dir / "skills", ai_dir)

    requirement_text = None
    if paths.requirement_md.is_file():
        requirement_text = _read_text(paths.requirement_md)

    memories: tuple[ContextFile, ...] = ()
    store = open_store_optional(root)
    if store is not None:
        try:
            with store.transaction():
                pid = ensure_project(store, name=config.project_name)
            memories = active_memories_for_context(store, pid)
        except Exception:
            memories = ()
        finally:
            store.close()

    return EASContext(
        root=root,
        paths=paths,
        config=config,
        rules=rules,
        skills=skills,
        requirement_text=requirement_text,
        memories=memories,
    )
