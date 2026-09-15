from __future__ import annotations

from eas.store.connection import Store
from eas.store.repository import fts_enabled


def search_context(
    store: Store,
    project_id: str,
    query: str,
    *,
    limit: int = 20,
) -> list[dict]:
    """Search memories, decisions, and messages (FTS or LIKE fallback)."""
    results: list[dict] = []
    q = query.strip()
    if not q:
        return results

    if fts_enabled(store):
        results.extend(
            _fts_search(store, project_id, q, limit=limit)
        )
    else:
        results.extend(
            _like_search(store, project_id, q, limit=limit)
        )
    return results[:limit]


def _fts_search(store: Store, project_id: str, query: str, limit: int) -> list[dict]:
    out: list[dict] = []
    # memories (active + candidate)
    rows = store._conn.execute(
        """
        SELECT m.id, m.state, m.content, memories_fts.rank
        FROM memories_fts
        JOIN memories m ON m.id = memories_fts.rowid
        WHERE memories_fts MATCH ? AND m.project_id = ?
        ORDER BY memories_fts.rank
        LIMIT ?
        """,
        (query, project_id, limit),
    ).fetchall()
    for r in rows:
        out.append(
            {
                "type": "memory",
                "id": r["id"],
                "state": r["state"],
                "snippet": r["content"][:240],
                "rank": r["rank"],
            }
        )

    rows = store._conn.execute(
        """
        SELECT d.id, d.kind, d.summary, decisions_fts.rank
        FROM decisions_fts
        JOIN decisions d ON d.id = decisions_fts.rowid
        WHERE decisions_fts MATCH ? AND d.project_id = ?
        ORDER BY decisions_fts.rank
        LIMIT ?
        """,
        (query, project_id, limit),
    ).fetchall()
    for r in rows:
        out.append(
            {
                "type": "decision",
                "id": r["id"],
                "kind": r["kind"],
                "snippet": r["summary"][:240],
                "rank": r["rank"],
            }
        )
    return out


def _like_search(store: Store, project_id: str, query: str, limit: int) -> list[dict]:
    pattern = f"%{query}%"
    out: list[dict] = []
    rows = store._conn.execute(
        """
        SELECT id, state, content FROM memories
        WHERE project_id = ? AND content LIKE ?
        LIMIT ?
        """,
        (project_id, pattern, limit),
    ).fetchall()
    for r in rows:
        out.append(
            {
                "type": "memory",
                "id": r["id"],
                "state": r["state"],
                "snippet": r["content"][:240],
                "rank": 0,
            }
        )
    rows = store._conn.execute(
        """
        SELECT id, kind, summary FROM decisions
        WHERE project_id = ? AND (summary LIKE ? OR detail LIKE ?)
        LIMIT ?
        """,
        (project_id, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        out.append(
            {
                "type": "decision",
                "id": r["id"],
                "kind": r["kind"],
                "snippet": r["summary"][:240],
                "rank": 0,
            }
        )
    return out
