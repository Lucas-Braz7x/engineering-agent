from __future__ import annotations

from pathlib import Path

from eas.runtime.llm import InvokeError, complete_agent
from eas.runtime.load_agent import load_agent
from eas.runtime.load_context import load_eas_context
from eas.runtime.models import AgentManifest, EASContext, InvokeResult, PrepareResult
from eas.runtime.prepare import prepare_agent_run


def _artifact_exists(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def run_prepare(
    *,
    root: Path,
    agent_id: str,
    run_id: str | None = None,
) -> PrepareResult:
    context = load_eas_context(root)
    agent = load_agent(root, agent_id)
    return prepare_agent_run(context=context, agent=agent, run_id=run_id)


def run_invoke(
    *,
    root: Path,
    agent_id: str,
    force: bool = False,
    run_id: str | None = None,
) -> InvokeResult:
    prepared = run_prepare(root=root, agent_id=agent_id, run_id=run_id)
    context = load_eas_context(root)
    agent = load_agent(root, agent_id)

    artifact_path = prepared.artifact_path
    if _artifact_exists(artifact_path) and not force:
        raise InvokeError(
            f"Artifact already exists: {artifact_path}. Use --force to overwrite."
        )

    prompt = prepared.invoke_path.read_text(encoding="utf-8")
    system = (
        f"You are the EAS {agent.id} agent. Output only the artifact markdown "
        f"(with eas-artifact YAML footer). No preamble."
    )
    output = complete_agent(system=system, user=prompt)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(output, encoding="utf-8")

    return InvokeResult(
        run_id=prepared.run_id,
        artifact_path=artifact_path,
        bytes_written=len(output.encode("utf-8")),
    )


def format_prepare_message(result: PrepareResult, root: Path) -> str:
    try:
        invoke_rel = result.invoke_path.relative_to(root)
        artifact_rel = result.artifact_path.relative_to(root)
    except ValueError:
        invoke_rel = result.invoke_path
        artifact_rel = result.artifact_path

    return (
        f"Prepared run {result.run_id}\n"
        f"Invoke bundle: {invoke_rel}\n"
        f"Target artifact: {artifact_rel}\n"
        "Next: paste invoke.md into your IDE, or run with --invoke (requires ANTHROPIC_API_KEY).\n"
    )


def format_invoke_message(result: InvokeResult, root: Path) -> str:
    try:
        artifact_rel = result.artifact_path.relative_to(root)
    except ValueError:
        artifact_rel = result.artifact_path
    return (
        f"Invoked run {result.run_id}\n"
        f"Wrote artifact: {artifact_rel} ({result.bytes_written} bytes)\n"
    )
