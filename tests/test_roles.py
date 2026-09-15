from pathlib import Path

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.runtime.load_agent import load_agent
from eas.runtime.validate_artifact import validate_artifact
from eas.tools.models import ToolContext
from eas.tools.registry import execute

runner = CliRunner()


def _minimal_repo(tmp_path: Path) -> Path:
    ai = tmp_path / ".ai"
    (ai / "agents").mkdir(parents=True)
    (ai / "workspace").mkdir()
    src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / "architect.md"
    (ai / "agents" / "architect.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (ai / "project.yaml").write_text("project:\n  name: t\n", encoding="utf-8")
    return tmp_path


def test_architect_cannot_write_source(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    agent = load_agent(root, "architect")
    ctx = ToolContext(root=root, config=None)

    blocked = execute(
        ctx,
        "write_file",
        agent=agent,
        path="src/main.py",
        content="hack",
    )
    assert not blocked.ok
    assert "not allowed" in (blocked.error or "")

    allowed = execute(
        ctx,
        "write_artifact",
        agent=agent,
        path=".ai/workspace/architecture.md",
        content="# Arch\n\n```yaml\nagent: architect\nstatus: draft\nrisk_level: low\n```\n",
    )
    assert allowed.ok


def test_architect_cannot_git_diff(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    agent = load_agent(root, "architect")
    ctx = ToolContext(root=root, config=None)
    result = execute(ctx, "git_diff", agent=agent)
    assert not result.ok
    assert "git_diff" in (result.error or "")


def test_invoke_prompt_lists_role_boundaries(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    from eas.runtime.build_prompt import build_invoke_prompt
    from eas.runtime.load_context import load_eas_context

    (root / ".ai" / "workspace" / "requirement.md").write_text("# R\n", encoding="utf-8")
    ctx = load_eas_context(root)
    agent = load_agent(root, "architect")
    prompt = build_invoke_prompt(context=ctx, agent=agent)
    assert "Role boundaries (code-enforced)" in prompt
    assert "write_artifact" in prompt
    assert "write_file" not in prompt.split("Allowed tools:")[1].split("Denied")[0]


def test_agent_show_cli(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    result = runner.invoke(app, ["agent", "show", "architect", "--path", str(root)])
    assert result.exit_code == 0
    assert "write_artifact" in result.stdout
    assert "review_peer" in result.stdout.lower() or "Review peer" in result.stdout


def test_validate_artifact_strict_sections(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    agent = load_agent(root, "architect")
    text = (
        "## Summary\n\nbody\n\n```yaml\n"
        "agent: architect\nstatus: draft\nrisk_level: low\n```\n"
    )
    loose = validate_artifact(text, agent, check_sections=False)
    assert loose == []
    strict = validate_artifact(text, agent, check_sections=True)
    assert any("Requirements" in err for err in strict)


def test_tools_agent_flag_blocks_write_file(tmp_path: Path):
    root = _minimal_repo(tmp_path)
    result = runner.invoke(
        app,
        [
            "tools",
            "--agent",
            "architect",
            "--path",
            str(root),
            "write-file",
            "foo.py",
            "--content",
            "x",
        ],
    )
    assert result.exit_code == 5
    assert "not allowed" in result.stderr
