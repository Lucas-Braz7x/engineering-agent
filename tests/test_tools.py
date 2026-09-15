from pathlib import Path

import pytest
from typer.testing import CliRunner

from eas.cli import app
from eas.context.loader import load_project_config
from eas.tools.models import ToolContext
from eas.tools.policy import ToolPolicyError, resolve_repo_path
from eas.tools.registry import execute

runner = CliRunner()


def _ctx(tmp_path: Path) -> ToolContext:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "project.yaml").write_text(
        "project:\n  name: t\ntesting:\n  command: echo tests-ok\n",
        encoding="utf-8",
    )
    config = load_project_config(tmp_path / ".ai" / "project.yaml")
    return ToolContext(root=tmp_path, config=config)


def test_resolve_path_blocks_escape(tmp_path: Path):
    with pytest.raises(ToolPolicyError):
        resolve_repo_path(tmp_path, "../../etc/passwd")


def test_read_and_write_file(tmp_path: Path):
    ctx = _ctx(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.txt").write_text("hello", encoding="utf-8")

    read = execute(ctx, "read_file", path="src/a.txt")
    assert read.ok
    assert "hello" in read.output

    write = execute(ctx, "write_file", path=".ai/workspace/out.md", content="# ok\n")
    assert write.ok
    assert (tmp_path / ".ai" / "workspace" / "out.md").read_text() == "# ok\n"


def test_write_blocked_under_git(tmp_path: Path):
    ctx = _ctx(tmp_path)
    (tmp_path / ".git").mkdir()
    result = execute(ctx, "write_file", path=".git/config", content="x")
    assert not result.ok
    assert ".git" in (result.error or "")


def test_search_code(tmp_path: Path):
    ctx = _ctx(tmp_path)
    (tmp_path / "lib.py").write_text("def unique_token_123():\n    pass\n", encoding="utf-8")
    result = execute(ctx, "search_code", pattern=r"unique_token_123", glob="*.py")
    assert result.ok
    assert "lib.py" in result.output


def test_run_command(tmp_path: Path):
    ctx = _ctx(tmp_path)
    result = execute(ctx, "run_command", command="echo hello-eas")
    assert result.ok
    assert "hello-eas" in result.output


def test_run_command_blocks_rm(tmp_path: Path):
    ctx = _ctx(tmp_path)
    result = execute(ctx, "run_command", command="rm -rf .")
    assert not result.ok


def test_run_tests_uses_project_yaml(tmp_path: Path):
    ctx = _ctx(tmp_path)
    result = execute(ctx, "run_tests")
    assert result.ok
    assert "tests-ok" in result.output


def test_git_status_in_repo(tmp_path: Path):
    ctx = _ctx(tmp_path)
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    result = execute(ctx, "git_status")
    assert result.ok


def test_tools_list_cli(tmp_path: Path):
    _ctx(tmp_path)
    result = runner.invoke(app, ["tools", "list", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "read_file" in result.stdout
    assert "git_diff" in result.stdout


def test_tools_read_file_cli(tmp_path: Path):
    _ctx(tmp_path)
    (tmp_path / "README.md").write_text("cli-read", encoding="utf-8")
    result = runner.invoke(
        app,
        ["tools", "read-file", "README.md", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "cli-read" in result.stdout
