from pathlib import Path

from typer.testing import CliRunner

from eas.cli import app
from eas.runtime.build_prompt import build_invoke_prompt
from eas.runtime.load_agent import load_agent
from eas.runtime.load_context import load_eas_context
from eas.store.connection import ensure_store
from eas.store.memory_service import active_memories_for_context
from eas.store.repository import add_memory, ensure_project, list_memories

runner = CliRunner()


def _repo(tmp_path: Path) -> Path:
    ai = tmp_path / ".ai"
    (ai / "agents").mkdir(parents=True)
    (ai / "workspace").mkdir()
    (ai / "project.yaml").write_text("project:\n  name: mem\n", encoding="utf-8")
    src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / "architect.md"
    (ai / "agents" / "architect.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (ai / "workspace" / "requirement.md").write_text("# R\n", encoding="utf-8")
    return tmp_path


def test_memory_promote_and_inject(tmp_path: Path):
    root = _repo(tmp_path)
    store = ensure_store(root)
    with store.transaction():
        pid = ensure_project(store)
        mid = add_memory(
            store,
            pid,
            content="This project uses Zod for validation.",
            state="candidate",
        )
        from eas.store.repository import update_memory_state

        update_memory_state(store, mid, "active")
    store.close()

    ctx = load_eas_context(root)
    assert len(ctx.memories) == 1
    assert "Zod" in ctx.memories[0].content

    agent = load_agent(root, "architect")
    prompt = build_invoke_prompt(context=ctx, agent=agent)
    assert "Project memories" in prompt
    assert "Zod" in prompt


def test_memory_cli_add_and_list(tmp_path: Path):
    root = _repo(tmp_path)
    add = runner.invoke(
        app,
        ["memory", "add", "Uses pytest for tests", "--path", str(root)],
    )
    assert add.exit_code == 0
    listed = runner.invoke(app, ["memory", "list", "--path", str(root)])
    assert listed.exit_code == 0
    assert "pytest" in listed.stdout


def test_validate_memory_strict(tmp_path: Path):
    root = _repo(tmp_path)
    store = ensure_store(root)
    with store.transaction():
        pid = ensure_project(store)
        rows = list_memories(store, pid, state="active")
    assert rows == []
    store.close()
