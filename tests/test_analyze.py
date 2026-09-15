from pathlib import Path

from typer.testing import CliRunner

from eas.cli import app

runner = CliRunner()


def _write_minimal_project(root: Path) -> None:
    ai = root / ".ai"
    ai.mkdir()
    (ai / "project.yaml").write_text(
        "project:\n  name: demo\nlanguage:\n  name: python\n",
        encoding="utf-8",
    )
    (ai / "workspace").mkdir()


def test_analyze_missing_project_yaml(tmp_path: Path):
    result = runner.invoke(app, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 2
    assert "Missing" in result.stderr
    assert "init" in result.stderr.lower()


def test_analyze_success(tmp_path: Path):
    _write_minimal_project(tmp_path)
    result = runner.invoke(app, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "EAS analyze" in result.stdout
    assert "Recommendation:" in result.stdout
    assert "Draft: not requested" in result.stdout
    assert "requirement: .ai/workspace/requirement.md" in result.stdout
    assert "architecture: .ai/workspace/architecture.md" in result.stdout
    assert "prompts.md" in result.stdout
    assert "architect.md" in result.stdout


def test_analyze_invalid_project_yaml_exit_1(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    invalid = Path(__file__).parent / "fixtures" / "project_yaml" / "invalid.yaml"
    (ai / "project.yaml").write_text(invalid.read_text(encoding="utf-8"), encoding="utf-8")
    (ai / "workspace").mkdir()

    result = runner.invoke(app, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "Invalid YAML" in result.stderr or "Invalid YAML" in result.stdout


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "0.1.0"


def test_analyze_write_draft(tmp_path: Path):
    _write_minimal_project(tmp_path)
    arch = tmp_path / ".ai" / "workspace" / "architecture.md"
    assert not arch.is_file()

    result = runner.invoke(app, ["analyze", "--path", str(tmp_path), "--write-draft"])
    assert result.exit_code == 0
    assert "Draft: created" in result.stdout
    assert arch.is_file()
    assert "architect" in arch.read_text(encoding="utf-8").lower()

    result2 = runner.invoke(app, ["analyze", "--path", str(tmp_path), "--write-draft"])
    assert result2.exit_code == 0
    assert "Draft: skipped (exists)" in result2.stdout


def test_find_repo_root_from_subdirectory(tmp_path: Path):
    _write_minimal_project(tmp_path)
    sub = tmp_path / "src" / "nested"
    sub.mkdir(parents=True)
    result = runner.invoke(app, ["analyze", "--path", str(sub)])
    assert result.exit_code == 0
    assert "Project: demo" in result.stdout
