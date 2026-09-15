"""
Template: avaliador local de agente (sem LLM).

Uso:
  python -m eas...  # ou script standalone copiado para scripts/eval_<agent>.py

Verifica:
- manifest YAML no .md do agente
- política de tools vs roles.py
- artefato de exemplo (opcional) com validate_artifact
"""
from __future__ import annotations

from pathlib import Path

from eas.runtime.load_agent import load_agent
from eas.runtime.roles import policy_for_agent
from eas.runtime.validate_artifact import validate_artifact


class EvaluationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors


def evaluate_agent_definition(root: Path, agent_id: str) -> EvaluationResult:
    result = EvaluationResult()
    try:
        manifest = load_agent(root, agent_id)
    except Exception as exc:
        result.errors.append(f"load_agent: {exc}")
        return result

    try:
        policy = policy_for_agent(agent_id)
    except KeyError:
        result.errors.append(f"No AGENT_ROLE_POLICIES entry for {agent_id}")
        return result

    if manifest.allowed_tools - policy.allowed_tools:
        extra = manifest.allowed_tools - policy.allowed_tools
        result.errors.append(f"Manifest allows tools not in policy: {sorted(extra)}")

    if not manifest.review_peer and agent_id in {"architect", "reviewer", "tester"}:
        result.warnings.append("review_peer not set — consider a review pair")

    if not manifest.artifact_path.startswith(".ai/workspace/"):
        result.warnings.append("artifact_path should live under .ai/workspace/")

    return result


def evaluate_artifact(root: Path, agent_id: str, artifact_path: Path) -> EvaluationResult:
    result = EvaluationResult()
    manifest = load_agent(root, agent_id)
    if not artifact_path.is_file():
        result.errors.append(f"Missing artifact: {artifact_path}")
        return result
    text = artifact_path.read_text(encoding="utf-8")
    for err in validate_artifact(text, manifest, check_sections=True):
        result.errors.append(err)
    return result


def main() -> int:
    import sys

    if len(sys.argv) < 3:
        print("Usage: evaluator.py <repo-root> <agent-id> [artifact.md]", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    agent_id = sys.argv[2]
    r1 = evaluate_agent_definition(root, agent_id)
    for w in r1.warnings:
        print(f"WARN: {w}")
    for e in r1.errors:
        print(f"ERROR: {e}")
    if len(sys.argv) >= 4:
        r2 = evaluate_artifact(root, agent_id, Path(sys.argv[3]))
        for e in r2.errors:
            print(f"ERROR: {e}")
        if not r2.ok:
            return 1
    return 0 if r1.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
