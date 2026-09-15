from pathlib import Path

from typer.testing import CliRunner

from eas.cli import app
from eas.loop.budget import LoopBlockedError, LoopBudget
from eas.context.limits import LoopLimits
from eas.loop.runner import run_autonomous_loop

runner = CliRunner()


def _seed(root: Path, *, test_cmd: str = "echo ok") -> None:
    ai = root / ".ai"
    (ai / "agents").mkdir(parents=True, exist_ok=True)
    (ai / "workspace").mkdir(parents=True, exist_ok=True)
    for name in ("debugger.md", "fixer.md", "reviewer.md"):
        src = Path(__file__).resolve().parents[1] / ".ai" / "agents" / name
        if src.is_file():
            (ai / "agents" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (ai / "project.yaml").write_text(
        f"project:\n  name: loop\ntesting:\n  command: {test_cmd}\n"
        "limits:\n  max_iterations: 2\n  max_command_execution: 10\n  max_agent_calls: 10\n",
        encoding="utf-8",
    )


def test_budget_blocks_iterations():
    budget = LoopBudget(limits=LoopLimits(max_iterations= 1))
    budget.begin_iteration()
    try:
        budget.begin_iteration()
        raise AssertionError("expected block")
    except LoopBlockedError as exc:
        assert "iterations" in exc.reason.lower()


def test_loop_success_when_tests_pass(tmp_path: Path):
    _seed(tmp_path, test_cmd="echo ok")
    outcome = run_autonomous_loop(tmp_path, invoke_agents=False, suggest_fix=False, review_on_success=False, force=False)
    assert outcome.status == "SUCCESS"
    assert (tmp_path / ".ai/workspace/loop-report.md").is_file()


def test_loop_tests_failed_without_agents(tmp_path: Path):
    _seed(tmp_path, test_cmd="python3 -c \"import sys; sys.exit(1)\"")
    outcome = run_autonomous_loop(tmp_path, invoke_agents=False, suggest_fix=False, review_on_success=False, force=False)
    assert outcome.status == "TESTS_FAILED"
    assert "invoke-agents" in outcome.reason


def test_loop_cli(tmp_path: Path):
    _seed(tmp_path)
    result = runner.invoke(app, ["loop", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout


def test_loop_invoke_debugger_on_failure(monkeypatch, tmp_path: Path):
    _seed(tmp_path, test_cmd="python3 -c \"import sys; sys.exit(1)\"")
    calls: list[str] = []

    def fake_invoke(*, root, agent_id, force=False, run_id=None, extra_sections=()):
        calls.append(agent_id)
        path = root / ".ai/workspace/debug-report.md"
        path.write_text("# debug\n", encoding="utf-8")

    monkeypatch.setattr("eas.loop.runner.run_invoke", fake_invoke)

    outcome = run_autonomous_loop(
        tmp_path,
        invoke_agents=True,
        suggest_fix=False,
        review_on_success=False,
        force=True,
        limits_override=LoopLimits(max_iterations=1, max_command_execution=5, max_agent_calls=5),
    )
    assert "debugger" in calls
    assert outcome.status == "WORKFLOW_BLOCKED"
