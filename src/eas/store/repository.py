from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from eas.store.connection import Store

MAX_MESSAGE_CHARS = 64_000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return uuid.uuid4().hex


def ensure_project(store: Store, *, name: str | None = None) -> str:
    root_str = store.root.as_posix()
    row = store._conn.execute(
        "SELECT id FROM projects WHERE root_path = ?", (root_str,)
    ).fetchone()
    if row:
        return str(row["id"])
    pid = _new_id()
    now = _utc_now()
    store._conn.execute(
        "INSERT INTO projects(id, root_path, name, created_at, updated_at) VALUES (?,?,?,?,?)",
        (pid, root_str, name, now, now),
    )
    return pid


def create_task(
    store: Store,
    project_id: str,
    *,
    kind: str,
    title: str | None,
    status: str = "running",
) -> str:
    tid = _new_id()
    now = _utc_now()
    store._conn.execute(
        """
        INSERT INTO tasks(id, project_id, kind, title, status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (tid, project_id, kind, title, status, now, now),
    )
    return tid


def update_task_status(store: Store, task_id: str, status: str) -> None:
    store._conn.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (status, _utc_now(), task_id),
    )


def create_run(
    store: Store,
    project_id: str,
    *,
    run_id: str,
    agent_id: str,
    kind: str,
    status: str,
    task_id: str | None = None,
    run_dir: str | None = None,
    artifact_path: str | None = None,
) -> str:
    now = _utc_now()
    store._conn.execute(
        """
        INSERT INTO runs(
            id, project_id, task_id, agent_id, kind, status,
            run_dir, artifact_path, created_at, finished_at
        ) VALUES (?,?,?,?,?,?,?,?,?,NULL)
        """,
        (
            run_id,
            project_id,
            task_id,
            agent_id,
            kind,
            status,
            run_dir,
            artifact_path,
            now,
        ),
    )
    return run_id


def update_run(
    store: Store,
    run_id: str,
    *,
    kind: str | None = None,
    status: str | None = None,
) -> None:
    if kind is not None and status is not None:
        store._conn.execute(
            "UPDATE runs SET kind = ?, status = ? WHERE id = ?",
            (kind, status, run_id),
        )
    elif status is not None:
        store._conn.execute(
            "UPDATE runs SET status = ? WHERE id = ?",
            (status, run_id),
        )


def finish_run(store: Store, run_id: str, status: str) -> None:
    store._conn.execute(
        "UPDATE runs SET status = ?, finished_at = ? WHERE id = ?",
        (status, _utc_now(), run_id),
    )


def add_message(store: Store, run_id: str, role: str, content: str) -> int:
    truncated = 0
    body = content
    if len(body) > MAX_MESSAGE_CHARS:
        body = body[:MAX_MESSAGE_CHARS] + "\n…(truncated)"
        truncated = 1
    now = _utc_now()
    cur = store._conn.execute(
        """
        INSERT INTO messages(run_id, role, content, content_truncated, created_at)
        VALUES (?,?,?,?,?)
        """,
        (run_id, role, body, truncated, now),
    )
    row_id = int(cur.lastrowid)
    _sync_message_fts(store, row_id, body)
    return row_id


def fts_enabled(store: Store) -> bool:
    row = store._conn.execute(
        "SELECT value FROM store_meta WHERE key = 'fts_enabled'"
    ).fetchone()
    return row is not None and row["value"] == "1"


def _sync_memory_fts(store: Store, row_id: int, content: str) -> None:
    if not fts_enabled(store):
        return
    store._conn.execute(
        "INSERT INTO memories_fts(rowid, content) VALUES (?,?)", (row_id, content)
    )


def _sync_decision_fts(store: Store, row_id: int, summary: str, detail: str | None) -> None:
    if not fts_enabled(store):
        return
    store._conn.execute(
        "INSERT INTO decisions_fts(rowid, summary, detail) VALUES (?,?,?)",
        (row_id, summary, detail or ""),
    )


def _sync_message_fts(store: Store, row_id: int, content: str) -> None:
    if not fts_enabled(store):
        return
    store._conn.execute(
        "INSERT INTO messages_fts(rowid, content) VALUES (?,?)", (row_id, content)
    )


def add_decision(
    store: Store,
    project_id: str,
    *,
    kind: str,
    summary: str,
    detail: str | None = None,
    run_id: str | None = None,
) -> int:
    cur = store._conn.execute(
        """
        INSERT INTO decisions(project_id, run_id, kind, summary, detail, created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (project_id, run_id, kind, summary, detail, _utc_now()),
    )
    row_id = int(cur.lastrowid)
    _sync_decision_fts(store, row_id, summary, detail)
    return row_id


def add_memory(
    store: Store,
    project_id: str,
    *,
    content: str,
    state: str,
    scope: str = "project",
    confidence: float = 0.5,
    source_kind: str | None = None,
    source_ref: str | None = None,
    expires_at: str | None = None,
) -> int:
    now = _utc_now()
    cur = store._conn.execute(
        """
        INSERT INTO memories(
            project_id, state, scope, content, confidence,
            source_kind, source_ref, created_at, updated_at, expires_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            project_id,
            state,
            scope,
            content.strip(),
            confidence,
            source_kind,
            source_ref,
            now,
            now,
            expires_at,
        ),
    )
    row_id = int(cur.lastrowid)
    _sync_memory_fts(store, row_id, content.strip())
    return row_id


def update_memory_state(store: Store, memory_id: int, state: str) -> None:
    store._conn.execute(
        "UPDATE memories SET state = ?, updated_at = ? WHERE id = ?",
        (state, _utc_now(), memory_id),
    )


def delete_memory(store: Store, memory_id: int) -> None:
    if _fts_enabled(store):
        store._conn.execute("DELETE FROM memories_fts WHERE rowid = ?", (memory_id,))
    store._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))


def list_memories(
    store: Store,
    project_id: str,
    *,
    state: str | None = None,
    limit: int = 100,
) -> list[dict]:
    if state:
        rows = store._conn.execute(
            """
            SELECT * FROM memories
            WHERE project_id = ? AND state = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (project_id, state, limit),
        ).fetchall()
    else:
        rows = store._conn.execute(
            """
            SELECT * FROM memories
            WHERE project_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def register_artifact(
    store: Store,
    run_id: str,
    relative_path: str,
    *,
    file_path: Path | None = None,
) -> int:
    sha = None
    size = None
    if file_path is not None and file_path.is_file():
        data = file_path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        size = len(data)
    cur = store._conn.execute(
        """
        INSERT INTO artifacts(run_id, relative_path, sha256, size_bytes, created_at)
        VALUES (?,?,?,?,?)
        """,
        (run_id, relative_path, sha, size, _utc_now()),
    )
    return int(cur.lastrowid)


def store_meta_get(store: Store, key: str) -> str | None:
    row = store._conn.execute(
        "SELECT value FROM store_meta WHERE key = ?", (key,)
    ).fetchone()
    return str(row["value"]) if row else None


def store_meta_set(store: Store, key: str, value: str) -> None:
    store._conn.execute(
        "INSERT OR REPLACE INTO store_meta(key, value) VALUES (?,?)", (key, value)
    )


def count_rows(store: Store) -> dict[str, int]:
    tables = ("projects", "tasks", "runs", "messages", "decisions", "memories", "artifacts")
    out: dict[str, int] = {}
    for table in tables:
        row = store._conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
        out[table] = int(row["c"])
    return out


def list_recent_runs(store: Store, project_id: str, limit: int = 20) -> list[dict]:
    rows = store._conn.execute(
        """
        SELECT * FROM runs
        WHERE project_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (project_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]
