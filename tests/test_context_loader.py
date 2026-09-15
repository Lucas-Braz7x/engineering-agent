from pathlib import Path

import pytest

from eas.context.loader import ProjectConfigError, load_project_config


FIXTURES = Path(__file__).parent / "fixtures" / "project_yaml"


def test_load_valid_project_yaml():
    config = load_project_config(FIXTURES / "valid.yaml")
    assert config.project_name == "file-uploader"
    assert config.language_name == "typescript"
    assert config.language_version == "22"
    assert config.framework_name == "nestjs"
    assert config.package_manager_name == "pnpm"
    assert config.database_name == "postgresql"
    assert config.testing_command == "pnpm test"
    assert config.build_command == "pnpm build"


def test_load_missing_file(tmp_path: Path):
    with pytest.raises(ProjectConfigError, match="Missing"):
        load_project_config(tmp_path / "missing.yaml")


def test_load_invalid_yaml():
    with pytest.raises(ProjectConfigError, match="Invalid YAML"):
        load_project_config(FIXTURES / "invalid.yaml")
