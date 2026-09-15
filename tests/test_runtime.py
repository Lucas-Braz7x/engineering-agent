from pathlib import Path

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.runtime.build_prompt import build_invoke_prompt
from eas.runtime.invoke import InvokeError, run_invoke, run_prepare
from eas.runtime.load_agent import AgentLoadError, load_agent
from eas.runtime.load_context import load_eas_context

runner = CliRunner()


def _seed_eas(root: Path) -> None:
    ai = root / ".ai"
    (ai / "agents").mkdir(parents=True)
    (ai / "rules").mkdir()
    (ai / "skills" / "general").mkdir(parents=True)
    (ai / "workspace").mkdir()

    architect_src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / "architect.md"
    (ai / "agents" / "architect.md").write_text(
        architect_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (ai / "rules" / "coding.md").write_text("# Coding\n", encoding="utf-8")
    (ai / "skills" / "general" / "README.md").write_text("# Skills\n", encoding="utf-8")
    (ai / "project.yaml").write_text(
        "project:\n  name: demo\nlanguage:\n  name: python\n",
        encoding="utf-8",
    )
    (ai / "workspace" / "requirement.md").write_text(
        "# Requirement\n\n## Title\n\nDemo feature\n",
        encoding="utf-8",
    )


def test_load_eas_context_counts(tmp_path: Path):
    _seed_eas(tmp_path)
    ctx = load_eas_context(tmp_path)
    assert len(ctx.rules) == 1
    assert len(ctx.skills) == 1
    assert ctx.requirement_text is not None


def test_build_invoke_prompt_includes_requirement(tmp_path: Path):
    _seed_eas(tmp_path)
    ctx = load_eas_context(tmp_path)
    agent = load_agent(tmp_path, "architect")
    prompt = build_invoke_prompt(context=ctx, agent=agent)
    assert "Demo feature" in prompt
    assert "Agent definition (full)" in prompt
    assert "rules/coding.md" in prompt


def test_prepare_writes_run_bundle(tmp_path: Path):
    _seed_eas(tmp_path)
    result = run_prepare(root=tmp_path, agent_id="architect", run_id="test-run")
    assert result.invoke_path.is_file()
    assert "invoke.md" in result.invoke_path.name
    assert (tmp_path / ".ai" / "workspace" / "runs" / "test-run" / "meta.yaml").is_file()


def test_analyze_agent_prepare_cli(tmp_path: Path):
    _seed_eas(tmp_path)
    result = runner.invoke(
        app,
        ["analyze", "--path", str(tmp_path), "--agent", "architect", "--prepare"],
    )
    assert result.exit_code == 0
    assert "Prepared run" in result.stdout
    assert (tmp_path / ".ai" / "workspace" / "runs").is_dir()


def test_analyze_agent_requires_prepare_or_invoke(tmp_path: Path):
    _seed_eas(tmp_path)
    result = runner.invoke(
        app,
        ["analyze", "--path", str(tmp_path), "--agent", "architect"],
    )
    assert result.exit_code == 1


def test_invoke_writes_artifact(monkeypatch, tmp_path: Path):
    _seed_eas(tmp_path)

    def fake_complete(*, system: str, user: str, model: str | None = None) -> str:
        return (
            "# Artifact\n\n```yaml\n"
            "agent: architect\n"
            "status: draft\n"
            "risk_level: low\n"
            "```\n"
        )

    monkeypatch.setattr("eas.runtime.invoke.complete_agent", fake_complete)

    result = run_invoke(root=tmp_path, agent_id="architect", run_id="invoke-run")
    assert result.artifact_path.is_file()
    assert "Artifact" in result.artifact_path.read_text(encoding="utf-8")


def test_invoke_refuses_existing_artifact(monkeypatch, tmp_path: Path):
    _seed_eas(tmp_path)
    arch = tmp_path / ".ai" / "workspace" / "architecture.md"
    arch.write_text("existing\n", encoding="utf-8")

    monkeypatch.setattr(
        "eas.runtime.invoke.complete_agent",
        lambda **_: "# New\n",
    )

    with pytest.raises(InvokeError, match="already exists"):
        run_invoke(root=tmp_path, agent_id="architect", run_id="blocked-run")


def test_prepare_uses_bundled_agent_without_repo_agents(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "workspace").mkdir()
    (ai / "project.yaml").write_text("project:\n  name: ext\n", encoding="utf-8")

    result = run_prepare(root=tmp_path, agent_id="architect", run_id="bundled-run")
    assert result.invoke_path.is_file()
    text = result.invoke_path.read_text(encoding="utf-8")
    assert "Agent definition (full)" in text
    assert "bundled with engineering-agent" in text or "architect" in text.lower()


def test_unknown_agent(tmp_path: Path):
    _seed_eas(tmp_path)
    with pytest.raises(AgentLoadError):
        load_agent(tmp_path, "coder")
