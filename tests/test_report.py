from pathlib import Path

from eas.analysis.report import build_report
from eas.context.loader import ProjectConfig
from eas.context.paths import workspace_paths


def test_build_report_empty_config_stack_placeholder(tmp_path: Path):
    root = tmp_path
    (root / ".ai" / "workspace").mkdir(parents=True)
    paths = workspace_paths(root)
    report = build_report(
        version="0.0.0",
        config=ProjectConfig(),
        paths=paths,
        draft_status="não solicitado",
    )
    assert "(nenhum campo de stack em project.yaml)" in report


def test_build_report_empty_project_yaml_via_analyze(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "project.yaml").write_text("{}\n", encoding="utf-8")
    (ai / "workspace").mkdir()

    from typer.testing import CliRunner

    from eas.cli import app

    result = CliRunner().invoke(app, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "(nenhum campo de stack em project.yaml)" in result.stdout
