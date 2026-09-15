from pathlib import Path

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.workflows.runner import WorkflowError, run_workflow_invoke

runner = CliRunner()


def _seed(root: Path) -> None:
    ai = root / ".ai"
    (ai / "agents").mkdir(parents=True)
    (ai / "workspace").mkdir(parents=True)
    architect_src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / "architect.md"
    for name in ("architect.md", "tester.md", "reviewer.md", "debugger.md"):
        src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / name
        if src.is_file():
            (ai / "agents" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (ai / "project.yaml").write_text(
        "project:\n  name: wf\nlanguage:\n  name: python\n",
        encoding="utf-8",
    )
    (ai / "workspace" / "requirement.md").write_text(
        "# Requirement\n\n## Title\n\nDemo\n",
        encoding="utf-8",
    )


def test_feature_prepare_all(tmp_path: Path):
    _seed(tmp_path)
    result = runner.invoke(
        app,
        ["feature", "--path", str(tmp_path), "--prepare", "--all"],
    )
    assert result.exit_code == 0
    assert result.stdout.count("Prepared run") == 3


def test_feature_invoke_tester_blocked_without_approval(tmp_path: Path, monkeypatch):
    _seed(tmp_path)

    def fake_complete(*, system: str, user: str, model: str | None = None) -> str:
        return "# artifact\n"

    monkeypatch.setattr("eas.runtime.invoke.complete_agent", fake_complete)

    result = runner.invoke(
        app,
        ["feature", "--path", str(tmp_path), "--invoke", "--step", "tester", "--force"],
    )
    assert result.exit_code == 6
    assert "approval" in result.stderr.lower()


def test_feature_invoke_tester_with_assume_approved(tmp_path: Path, monkeypatch):
    _seed(tmp_path)

    def fake_complete(*, system: str, user: str, model: str | None = None) -> str:
        return "# test plan\n```yaml\nagent: tester\n```\n"

    monkeypatch.setattr("eas.runtime.invoke.complete_agent", fake_complete)

    result = runner.invoke(
        app,
        [
            "feature",
            "--path",
            str(tmp_path),
            "--invoke",
            "--step",
            "tester",
            "--force",
            "--assume-approved",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / ".ai" / "workspace" / "test-plan.md").is_file()


def test_review_invoke(monkeypatch, tmp_path: Path):
    _seed(tmp_path)
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

    def fake_complete(*, system: str, user: str, model: str | None = None) -> str:
        assert "Git diff" in user or "git" in user.lower()
        return "# review\n```yaml\nagent: reviewer\nstatus: APPROVED\n```\n"

    monkeypatch.setattr("eas.runtime.invoke.complete_agent", fake_complete)

    result = runner.invoke(
        app,
        [
            "review",
            "--path",
            str(tmp_path),
            "--invoke",
            "--force",
            "--git-base",
            "HEAD",
            "--git-head",
            "HEAD",
        ],
    )
    assert result.exit_code == 0


def test_bug_writes_report_and_prepare_debugger(tmp_path: Path):
    _seed(tmp_path)
    result = runner.invoke(
        app,
        ["bug", "null pointer in handler", "--path", str(tmp_path), "--prepare", "--step", "debugger"],
    )
    assert result.exit_code == 0
    text = (tmp_path / ".ai" / "workspace" / "bug-report.md").read_text(encoding="utf-8")
    assert "null pointer" in text


def test_status_command(tmp_path: Path):
    _seed(tmp_path)
    result = runner.invoke(app, ["status", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "requirement.md" in result.stdout


def test_workflow_unknown_step(tmp_path: Path):
    _seed(tmp_path)
    with pytest.raises(WorkflowError):
        run_workflow_invoke(
            root=tmp_path,
            workflow_id="feature",
            step="coder",
            force=True,
            assume_approved=True,
        )
