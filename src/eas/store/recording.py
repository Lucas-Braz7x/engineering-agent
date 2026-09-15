from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from eas.store.connection import Store, open_store_optional
from eas.store.memory_service import ingest_artifact_candidates
from eas.store.repository import (
    add_decision,
    add_message,
    create_run,
    create_task,
    ensure_project,
    finish_run,
    register_artifact,
    update_run,
    update_task_status,
)
from eas.store.retention import maybe_auto_prune, policy_from_dict


@dataclass
class RecordingSession:
    store: Store
    project_id: str
    task_id: str | None = None


def _retention_policy_from_root(root: Path) -> dict | None:
    path = root / ".ai" / "project.yaml"
    if not path.is_file():
        return None
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    ctx = data.get("context")
    if isinstance(ctx, dict):
        ret = ctx.get("retention")
        if isinstance(ret, dict):
            return ret
    return None


def begin_session(root: Path, *, project_name: str | None = None) -> RecordingSession | None:
    store = open_store_optional(root)
    if store is None:
        return None
    with store.transaction():
        project_id = ensure_project(store, name=project_name)
        policy = policy_from_dict(_retention_policy_from_root(root))
        maybe_auto_prune(store, project_id, policy)
    return RecordingSession(store=store, project_id=project_id)


@contextmanager
def task_scope(
    session: RecordingSession | None,
    *,
    kind: str,
    title: str | None,
):
    if session is None:
        yield None
        return
    with session.store.transaction():
        tid = create_task(
            session.store,
            session.project_id,
            kind=kind,
            title=title,
            status="running",
        )
        session.task_id = tid
    try:
        yield tid
        with session.store.transaction():
            update_task_status(session.store, tid, "done")
    except Exception:
        with session.store.transaction():
            update_task_status(session.store, tid, "failed")
        raise


def record_prepare(
    session: RecordingSession | None,
    *,
    run_id: str,
    agent_id: str,
    run_dir: str,
    artifact_path: str,
) -> None:
    if session is None:
        return
    with session.store.transaction():
        create_run(
            session.store,
            session.project_id,
            run_id=run_id,
            agent_id=agent_id,
            kind="prepare",
            status="prepared",
            task_id=session.task_id,
            run_dir=run_dir,
            artifact_path=artifact_path,
        )


def record_invoke_start(
    session: RecordingSession | None,
    *,
    run_id: str,
    agent_id: str,
    system: str,
    user_prompt: str,
    artifact_path: str,
) -> None:
    if session is None:
        return
    with session.store.transaction():
        update_run(
            session.store,
            run_id,
            kind="invoke",
            status="running",
        )
        add_message(session.store, run_id, "system", system)
        add_message(session.store, run_id, "user", user_prompt)


def record_invoke_success(
    session: RecordingSession | None,
    *,
    run_id: str,
    agent_id: str,
    output: str,
    artifact_rel: str,
    artifact_file: Path,
    root: Path,
) -> None:
    if session is None:
        return
    with session.store.transaction():
        add_message(session.store, run_id, "assistant", output)
        finish_run(session.store, run_id, "invoked")
        register_artifact(
            session.store,
            run_id,
            artifact_rel,
            file_path=artifact_file,
        )
        add_decision(
            session.store,
            session.project_id,
            kind="artifact_written",
            summary=f"{agent_id} wrote {artifact_rel}",
            run_id=run_id,
        )
        ingest_artifact_candidates(
            session.store,
            session.project_id,
            output,
            source_ref=artifact_rel,
        )


def record_invoke_failed(session: RecordingSession | None, run_id: str, reason: str) -> None:
    if session is None:
        return
    with session.store.transaction():
        finish_run(session.store, run_id, "failed")
        add_decision(
            session.store,
            session.project_id,
            kind="invoke_failed",
            summary=reason[:500],
            run_id=run_id,
        )
