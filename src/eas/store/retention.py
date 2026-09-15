from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from eas.store.connection import Store
from eas.store.repository import _utc_now, store_meta_get, store_meta_set


@dataclass(frozen=True)
class RetentionPolicy:
    run_retention_days: int = 30
    min_recent_runs: int = 20
    candidate_retention_days: int = 14
    auto_prune_interval_hours: int = 24


def policy_from_dict(data: dict | None) -> RetentionPolicy:
    if not data:
        return RetentionPolicy()
    return RetentionPolicy(
        run_retention_days=int(data.get("run_retention_days", 30)),
        min_recent_runs=int(data.get("min_recent_runs", 20)),
        candidate_retention_days=int(data.get("candidate_retention_days", 14)),
        auto_prune_interval_hours=int(data.get("auto_prune_interval_hours", 24)),
    )


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


@dataclass(frozen=True)
class PrunePlan:
    runs_to_delete: list[str]
    messages_to_delete: int
    candidates_to_delete: list[int]


def plan_prune(store: Store, project_id: str, policy: RetentionPolicy) -> PrunePlan:
    now = datetime.now(timezone.utc)
    run_cutoff = now - timedelta(days=policy.run_retention_days)
    cand_cutoff = now - timedelta(days=policy.candidate_retention_days)

    recent = store._conn.execute(
        """
        SELECT id FROM runs
        WHERE project_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (project_id, policy.min_recent_runs),
    ).fetchall()
    protected = {str(r["id"]) for r in recent}

    rows = store._conn.execute(
        "SELECT id, created_at FROM runs WHERE project_id = ?", (project_id,)
    ).fetchall()
    runs_to_delete: list[str] = []
    for r in rows:
        rid = str(r["id"])
        if rid in protected:
            continue
        created = _parse_iso(str(r["created_at"]))
        if created < run_cutoff:
            runs_to_delete.append(rid)

    msg_count = 0
    if runs_to_delete:
        placeholders = ",".join("?" for _ in runs_to_delete)
        row = store._conn.execute(
            f"SELECT COUNT(*) AS c FROM messages WHERE run_id IN ({placeholders})",
            runs_to_delete,
        ).fetchone()
        msg_count = int(row["c"])

    cand_rows = store._conn.execute(
        """
        SELECT id, created_at FROM memories
        WHERE project_id = ? AND state = 'candidate'
        """,
        (project_id,),
    ).fetchall()
    candidates_to_delete: list[int] = []
    for r in cand_rows:
        created = _parse_iso(str(r["created_at"]))
        if created < cand_cutoff:
            candidates_to_delete.append(int(r["id"]))

    return PrunePlan(
        runs_to_delete=runs_to_delete,
        messages_to_delete=msg_count,
        candidates_to_delete=candidates_to_delete,
    )


def apply_prune(store: Store, plan: PrunePlan) -> None:
    for mid in plan.candidates_to_delete:
        store._conn.execute("DELETE FROM memories WHERE id = ?", (mid,))
    for rid in plan.runs_to_delete:
        store._conn.execute("DELETE FROM runs WHERE id = ?", (rid,))


def maybe_auto_prune(
    store: Store,
    project_id: str,
    policy: RetentionPolicy,
) -> PrunePlan | None:
    last = store_meta_get(store, "last_auto_prune_at")
    now = datetime.now(timezone.utc)
    if last:
        if now - _parse_iso(last) < timedelta(hours=policy.auto_prune_interval_hours):
            return None
    plan = plan_prune(store, project_id, policy)
    if plan.runs_to_delete or plan.candidates_to_delete:
        apply_prune(store, plan)
    store_meta_set(store, "last_auto_prune_at", _utc_now())
    return plan


def vacuum_db(store: Store) -> int:
    size_before = store.db_path.stat().st_size if store.db_path.is_file() else 0
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    store._conn.execute("VACUUM")
    size_after = store.db_path.stat().st_size
    return size_before - size_after
