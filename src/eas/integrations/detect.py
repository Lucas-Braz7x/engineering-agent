from __future__ import annotations

from pathlib import Path

from eas.integrations.proc import which_or_error


def detect_integration_signals(root: Path) -> list[str]:
    signals: list[str] = []

    if (root / ".git").exists():
        signals.append("Git repository")

    workflows = root / ".github" / "workflows"
    if workflows.is_dir() and (
        any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
    ):
        signals.append("GitHub Actions")
        if which_or_error("gh"):
            signals.append("gh CLI")

    for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml"):
        if (root / name).is_file():
            signals.append(f"Docker Compose ({name})")
            break
    if (root / "Dockerfile").is_file():
        signals.append("Dockerfile")

    if which_or_error("docker"):
        signals.append("docker CLI")

    if (root / ".aws").is_dir() or (root / "cdk.json").is_file():
        signals.append("AWS project hints")
    if which_or_error("aws"):
        signals.append("aws CLI")

    return signals
