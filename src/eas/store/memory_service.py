from __future__ import annotations

import re

from eas.runtime.models import ContextFile
from eas.store.connection import Store
from eas.store.repository import add_memory, list_memories

MEMORY_INJECT_MAX_ITEMS = 12
MEMORY_INJECT_MAX_CHARS = 4_000

# Heuristic lines from artifacts that may become memory candidates.
_CANDIDATE_PATTERNS = (
    re.compile(r"uses?\s+(\w+)\s+for\s+validation", re.I),
    re.compile(r"this project uses?\s+(.{3,80})", re.I),
    re.compile(r"stack:\s*(.+)", re.I),
)


def active_memories_for_context(
    store: Store,
    project_id: str,
) -> tuple[ContextFile, ...]:
    rows = list_memories(store, project_id, state="active", limit=MEMORY_INJECT_MAX_ITEMS)
    files: list[ContextFile] = []
    total = 0
    for row in rows:
        content = str(row["content"]).strip()
        if not content:
            continue
        line = f"- (id={row['id']}, source={row.get('source_kind') or 'unknown'}) {content}"
        if total + len(line) > MEMORY_INJECT_MAX_CHARS:
            break
        total += len(line)
        files.append(
            ContextFile(
                relative_path=f".eas/memories/{row['id']}.md",
                content=line,
            )
        )
    return tuple(files)


def extract_memory_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) < 12:
            continue
        for pat in _CANDIDATE_PATTERNS:
            if pat.search(stripped):
                candidates.append(stripped[:500])
                break
    return candidates


def ingest_artifact_candidates(
    store: Store,
    project_id: str,
    artifact_text: str,
    *,
    source_ref: str,
) -> int:
    seen = 0
    for line in extract_memory_candidates(artifact_text):
        add_memory(
            store,
            project_id,
            content=line,
            state="candidate",
            confidence=0.4,
            source_kind="artifact",
            source_ref=source_ref,
        )
        seen += 1
    return seen
