from pathlib import Path

from eas.analysis.purpose import gather_project_purpose, format_purpose_block
from eas.context.paths import workspace_paths


def test_purpose_from_readme_and_requirement(tmp_path: Path):
    root = tmp_path
    (root / ".ai" / "workspace").mkdir(parents=True)
    (root / ".ai" / "project.yaml").write_text(
        "project:\n  name: demo\n  description: Aplicativo demo para uploads\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Demo\n\nServiço que gerencia uploads para equipes.\n\n## Instalação\n\n```bash\npip install\n```\n",
        encoding="utf-8",
    )
    req = (
        "# Requisito\n\n## Problema\n\nUsuários não conseguem compartilhar arquivos grandes.\n\n"
        "## História de usuário\n\nComo dev, quero enviar arquivos com segurança.\n"
    )
    paths = workspace_paths(root)
    purpose = gather_project_purpose(root, paths, req)
    block = format_purpose_block(purpose)
    assert "Propósito:" in block
    assert "Problema que resolve:" in block
    assert "Para quem:" in block
    assert "Fonte:" in block
    assert "upload" in block.lower() or "arquivo" in block.lower()


def test_analyze_includes_purpose_section(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "workspace").mkdir()
    (ai / "project.yaml").write_text("project:\n  name: x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# X\n\nEste projeto oferece ferramentas de agentes de engenharia.\n",
        encoding="utf-8",
    )
    from typer.testing import CliRunner
    from eas.cli import app

    result = CliRunner().invoke(app, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Propósito:" in result.stdout
    assert "Resumo:" in result.stdout
    assert "agentes" in result.stdout.lower()
