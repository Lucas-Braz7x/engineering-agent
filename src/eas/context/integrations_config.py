from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntegrationsConfig:
    github_remote: str = "origin"
    docker_compose_file: str = "docker-compose.yml"
    aws_profile: str | None = None
    ci_provider: str = "github_actions"


def parse_integrations(data: dict[str, Any]) -> IntegrationsConfig | None:
    block = data.get("integrations")
    if not isinstance(block, dict):
        return None
    gh = block.get("github") if isinstance(block.get("github"), dict) else {}
    docker = block.get("docker") if isinstance(block.get("docker"), dict) else {}
    aws = block.get("aws") if isinstance(block.get("aws"), dict) else {}
    ci = block.get("ci") if isinstance(block.get("ci"), dict) else {}
    return IntegrationsConfig(
        github_remote=str(gh.get("remote", "origin")),
        docker_compose_file=str(docker.get("compose_file", "docker-compose.yml")),
        aws_profile=str(aws["profile"]) if aws.get("profile") else None,
        ci_provider=str(ci.get("provider", "github_actions")),
    )
