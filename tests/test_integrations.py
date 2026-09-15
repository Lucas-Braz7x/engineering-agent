from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.context.integrations_config import parse_integrations
from eas.context.loader import load_project_config
from eas.integrations.detect import detect_integration_signals
from eas.integrations.proc import run_argv
from eas.tools.models import ToolContext
from eas.tools.registry import execute, list_tools

runner = CliRunner()


def test_parse_integrations():
    cfg = parse_integrations(
        {
            "integrations": {
                "github": {"remote": "upstream"},
                "docker": {"compose_file": "compose.yaml"},
                "aws": {"profile": "dev"},
                "ci": {"provider": "github_actions"},
            }
        }
    )
    assert cfg is not None
    assert cfg.github_remote == "upstream"
    assert cfg.docker_compose_file == "compose.yaml"
    assert cfg.aws_profile == "dev"


def test_loader_reads_integrations(tmp_path: Path):
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "project.yaml").write_text(
        "project:\n  name: x\nintegrations:\n  github:\n    remote: origin\n",
        encoding="utf-8",
    )
    cfg = load_project_config(tmp_path / ".ai" / "project.yaml")
    assert cfg.integrations is not None
    assert cfg.integrations.github_remote == "origin"


def test_detect_signals_github_actions(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("on: push\n", encoding="utf-8")
    signals = detect_integration_signals(tmp_path)
    assert "Git repository" in signals
    assert "GitHub Actions" in signals


def test_run_argv_rejects_unknown_binary(tmp_path: Path):
    result = run_argv(["curl", "example.com"], cwd=tmp_path)
    assert not result.ok
    assert "not allowed" in (result.error or "")


def test_ci_workflow_files_tool(tmp_path: Path):
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "build.yml").write_text("", encoding="utf-8")
    ctx = ToolContext(root=tmp_path, config=None)
    result = execute(ctx, "ci_workflow_files")
    assert result.ok
    assert "build.yml" in result.output


def test_catalog_includes_integration_tools():
    names = {name for name, _ in list_tools()}
    assert "github_remote" in names
    assert "ci_github_runs" in names


@patch("eas.integrations.proc.which_or_error", return_value="/usr/bin/gh")
@patch("eas.integrations.proc.subprocess.run")
def test_ci_github_runs_mock(mock_run, _which, tmp_path: Path):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "run-id\tok"
    mock_run.return_value.stderr = ""
    ctx = ToolContext(root=tmp_path, config=None)
    result = execute(ctx, "ci_github_runs", limit=3)
    assert result.ok
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0][:3] == ["gh", "run", "list"]


@patch("eas.integrations.github_tool.subprocess.run")
def test_github_remote(mock_run, tmp_path: Path):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "git@github.com:org/repo.git\n"
    mock_run.return_value.stderr = ""
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "project.yaml").write_text(
        "project:\n  name: t\nintegrations:\n  github:\n    remote: origin\n",
        encoding="utf-8",
    )
    config = load_project_config(tmp_path / ".ai" / "project.yaml")
    ctx = ToolContext(root=tmp_path, config=config)
    result = execute(ctx, "github_remote")
    assert result.ok
    assert "github.com" in result.output


def test_integrations_status_cli(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    result = runner.invoke(app, ["integrations", "status", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Git repository" in result.stdout
