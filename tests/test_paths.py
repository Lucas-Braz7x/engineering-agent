from pathlib import Path

from eas.context.paths import find_repo_root


def test_find_repo_root_without_ai_returns_start(tmp_path: Path):
    sub = tmp_path / "no-ai-here"
    sub.mkdir()
    assert find_repo_root(sub) == sub.resolve()
