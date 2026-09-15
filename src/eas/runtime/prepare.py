from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from eas.runtime.build_prompt import build_invoke_prompt
from eas.runtime.models import AgentManifest, EASContext, PrepareResult


def new_run_id(agent_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{agent_id}"


def prepare_agent_run(
    *,
    context: EASContext,
    agent: AgentManifest,
    run_id: str | None = None,
) -> PrepareResult:
    run_id = run_id or new_run_id(agent.id)
    run_dir = context.root / ".ai" / "workspace" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    invoke_path = run_dir / "invoke.md"
    invoke_path.write_text(
        build_invoke_prompt(context=context, agent=agent),
        encoding="utf-8",
    )

    artifact_path = context.root / agent.artifact_path
    meta = run_dir / "meta.yaml"
    meta.write_text(
        f"agent: {agent.id}\nartifact_path: {agent.artifact_path}\n",
        encoding="utf-8",
    )

    return PrepareResult(
        run_id=run_id,
        run_dir=run_dir,
        invoke_path=invoke_path,
        artifact_path=artifact_path,
    )
