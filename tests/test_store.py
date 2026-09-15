from pathlib import Path

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.store.connection import ensure_store, is_context_enabled
from eas.store.repository import add_memory, ensure_project, list_memories
from eas.store.retention import apply_prune, plan_prune, policy_from_dict

runner = CliRunner()


def _repo(tmp_path: Path) -> Path:
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "workspace").mkdir()
    (ai / "project.yaml").write_text("project:\n  name: store-test\n", encoding="utf-8")
    return tmp_path


def test_ensure_store_idempotent(tmp_path: Path):
    root = _repo(tmp_path)
    s1 = ensure_store(root)
    s2 = ensure_store(root)
    assert s1 is not None and s2 is not None
    assert s1.db_path == s2.db_path
    assert s1.db_path.is_file()
    s1.close()
    s2.close()


def test_migrations_and_project_row(tmp_path: Path):
    root = _repo(tmp_path)
    store = ensure_store(root)
    with store.transaction():
        pid = ensure_project(store, name="demo")
        pid2 = ensure_project(store, name="demo")
    assert pid == pid2
    store.close()


def test_context_status_cli(tmp_path: Path):
    root = _repo(tmp_path)
    ensure_store(root).close()
    result = runner.invoke(app, ["context", "status", "--path", str(root)])
    assert result.exit_code == 0
    assert "runs:" in result.stdout or "Store:" in result.stdout


def test_prune_dry_run(tmp_path: Path):
    root = _repo(tmp_path)
    store = ensure_store(root)
    with store.transaction():
        pid = ensure_project(store)
        add_memory(store, pid, content="candidate line", state="candidate")
    plan = plan_prune(store, pid, policy_from_dict({"candidate_retention_days": 0}))
    assert plan.candidates_to_delete
    with store.transaction():
        apply_prune(store, plan)
    with store.transaction():
        left = list_memories(store, pid, state="candidate")
    assert left == []
    store.close()


def test_context_disabled_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("EAS_CONTEXT", "0")
    root = _repo(tmp_path)
    assert is_context_enabled(root) is False
    assert ensure_store(root) is None
