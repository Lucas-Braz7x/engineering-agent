from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from eas.store.migrations import CURRENT_VERSION, apply_migrations


class StoreError(Exception):
    pass


def is_context_enabled(root: Path) -> bool:
    if os.environ.get("EAS_CONTEXT", "1").strip() in {"0", "false", "no"}:
        return False
    return True


def eas_db_path(root: Path) -> Path:
    return root / ".eas" / "eas.db"


def ensure_eas_dir(root: Path) -> Path:
    eas = root / ".eas"
    eas.mkdir(parents=True, exist_ok=True)
    return eas


@dataclass
class Store:
    root: Path
    db_path: Path
    _conn: sqlite3.Connection

    @contextmanager
    def transaction(self):
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        self._conn.close()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def ensure_store(root: Path) -> Store | None:
    """Open or create the store; return None if context system is disabled."""
    if not is_context_enabled(root):
        return None
    try:
        ensure_eas_dir(root)
        db_path = eas_db_path(root)
        conn = _connect(db_path)
        apply_migrations(conn)
        return Store(root=root.resolve(), db_path=db_path, _conn=conn)
    except (sqlite3.Error, OSError) as exc:
        raise StoreError(f"Failed to open context store: {exc}") from exc


def open_store_optional(root: Path) -> Store | None:
    """Like ensure_store but swallows errors for degraded mode."""
    if not is_context_enabled(root):
        return None
    try:
        return ensure_store(root)
    except StoreError:
        return None
