from pathlib import Path

import yaml
from typer.testing import CliRunner

from eas.cli import app
from eas.detection.detect import detect_project

runner = CliRunner()


def test_detect_python_project(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "my-app"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.1"]
""".strip(),
        encoding="utf-8",
    )
    result = detect_project(tmp_path)
    assert result.project_name == "my-app"
    assert result.language_name == "python"
    assert result.language_version == "3.12"
    assert result.framework_name == "fastapi"


def test_init_creates_project_yaml(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\nrequires-python = '>=3.11'\n",
        encoding="utf-8",
    )
    invoke = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert invoke.exit_code == 0
    assert "Detecting project" in invoke.stdout
    assert "✓" in invoke.stdout

    yaml_path = tmp_path / ".ai" / "project.yaml"
    assert yaml_path.is_file()
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert data["project"]["name"] == "demo"
    assert data["language"]["name"] == "python"
    assert (tmp_path / ".ai" / "workspace").is_dir()


def test_init_refuses_overwrite_without_force(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'a'\n", encoding="utf-8")
    runner.invoke(app, ["init", "--path", str(tmp_path)])
    second = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert second.exit_code == 3
    assert "already exists" in second.stderr


def test_init_force_overwrites(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'first'\n", encoding="utf-8")
    runner.invoke(app, ["init", "--path", str(tmp_path)])
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'second'\n", encoding="utf-8")
    result = runner.invoke(app, ["init", "--path", str(tmp_path), "--force"])
    assert result.exit_code == 0
    data = yaml.safe_load((tmp_path / ".ai" / "project.yaml").read_text(encoding="utf-8"))
    assert data["project"]["name"] == "second"


def test_init_dry_run_no_write(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'dry'\n", encoding="utf-8")
    result = runner.invoke(app, ["init", "--path", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.stdout
    assert not (tmp_path / ".ai" / "project.yaml").exists()


def test_init_node_project(tmp_path: Path):
    (tmp_path / "package.json").write_text(
        '{"name":"web","devDependencies":{"typescript":"^5.0","@nestjs/core":"^10"},"scripts":{"test":"jest"}}',
        encoding="utf-8",
    )
    (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")
    result = runner.invoke(app, ["init", "--path", str(tmp_path)])
    assert result.exit_code == 0
    data = yaml.safe_load((tmp_path / ".ai" / "project.yaml").read_text(encoding="utf-8"))
    assert data["language"]["name"] == "typescript"
    assert data["framework"]["name"] == "nestjs"
    assert data["package_manager"]["name"] == "pnpm"
    assert data["testing"]["command"] == "pnpm test"


def test_detect_rust_project(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text(
        """
[package]
name = "api"
version = "0.1.0"
rust-version = "1.75"

[dependencies]
axum = "0.7"
""".strip(),
        encoding="utf-8",
    )
    result = detect_project(tmp_path)
    assert result.language_name == "rust"
    assert result.framework_name == "axum"
    assert result.testing_command == "cargo test"
    assert "Rust" in result.signals


def test_detect_maven_project(tmp_path: Path):
    (tmp_path / "pom.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<project>
  <artifactId>billing-service</artifactId>
  <properties><java.version>21</java.version></properties>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )
    result = detect_project(tmp_path)
    assert result.project_name == "billing-service"
    assert result.language_name == "java"
    assert result.framework_name == "spring-boot"
    assert result.package_manager_name == "maven"


def test_monorepo_merges_signals(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'platform'\nrequires-python = '>=3.11'\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        '{"name":"web","devDependencies":{"typescript":"^5"}}',
        encoding="utf-8",
    )
    result = detect_project(tmp_path)
    assert result.monorepo is True
    assert result.manifests == ["pyproject.toml", "package.json"]
    assert result.language_name == "python"
    assert "Python" in result.signals
    assert "TypeScript" in result.signals

    invoke = runner.invoke(app, ["init", "--path", str(tmp_path), "--force"])
    assert invoke.exit_code == 0
    assert "Monorepo:" in invoke.stdout
    data = yaml.safe_load((tmp_path / ".ai" / "project.yaml").read_text(encoding="utf-8"))
    assert data["detection"]["monorepo"] is True
    assert "package.json" in data["detection"]["manifests"]
