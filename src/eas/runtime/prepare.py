from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from eas.runtime.build_prompt import build_invoke_prompt
from eas.runtime.models import AgentManifest, EASContext, PrepareResult
from eas.store.recording import begin_session, record_prepare


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
    allowed = "\n".join(f"  - {name}" for name in sorted(agent.allowed_tools))
    session = begin_session(context.root, project_name=context.config.project_name)
    try:
        rel_run = run_dir.relative_to(context.root).as_posix()
    except ValueError:
        rel_run = str(run_dir)
    record_prepare(
        session,
        run_id=run_id,
        agent_id=agent.id,
        run_dir=rel_run,
        artifact_path=agent.artifact_path,
    )

    meta.write_text(
        (
            f"agent: {agent.id}\n"
            f"role: {agent.role_id}\n"
            f"review_peer: {agent.review_peer or ''}\n"
            f"artifact_path: {agent.artifact_path}\n"
            f"allowed_tools:\n{allowed}\n"
        ),
        encoding="utf-8",
    )

    return PrepareResult(
        run_id=run_id,
        run_dir=run_dir,
        invoke_path=invoke_path,
        artifact_path=artifact_path,
    )
