from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths
from eas.runtime.invoke import InvokeError, run_invoke, run_prepare
from eas.runtime.load_context import load_eas_context
from eas.runtime.models import InvokeResult, PrepareResult
from eas.workflows.approval import approval_hint, architecture_approved
from eas.workflows.context_bundle import gather_git_context, read_bug_report, write_bug_report
from eas.workflows.specs import WORKFLOWS, WorkflowSpec
from eas.store.recording import begin_session, task_scope


class WorkflowError(Exception):
    pass


@dataclass(frozen=True)
class WorkflowRunSummary:
    workflow_id: str
    prepared: tuple[PrepareResult, ...]
    invoked: tuple[InvokeResult, ...]


def _resolve_steps(spec: WorkflowSpec, step: str | None, run_all: bool) -> tuple[str, ...]:
    if run_all:
        return spec.steps
    if step:
        if step not in spec.steps:
            raise WorkflowError(
                f"Unknown step {step!r} for workflow {spec.id}. "
                f"Valid: {', '.join(spec.steps)}"
            )
        return (step,)
    return (spec.steps[0],)


def _extra_sections_for_agent(
    root: Path,
    agent_id: str,
    *,
    config,
    git_base: str | None,
    git_head: str | None,
    with_tests: bool,
) -> tuple[tuple[str, str], ...]:
    sections: list[tuple[str, str]] = []
    if agent_id == "debugger":
        bug = read_bug_report(root)
        if bug:
            sections.append(("Bug report", bug))
    if agent_id in {"tester", "reviewer", "debugger"}:
        sections.extend(
            gather_git_context(
                root,
                config,
                git_base=git_base,
                git_head=git_head,
                include_tests=with_tests and agent_id == "reviewer",
            )
        )
    return tuple(sections)


def _gate_approval(spec: WorkflowSpec, agent_id: str, root: Path, assume_approved: bool) -> None:
    if agent_id not in spec.requires_approval_before:
        return
    if assume_approved:
        return
    if spec.id == "feature" and not architecture_approved(root):
        raise WorkflowError(approval_hint())
    if spec.id == "bug":
        debug = root / ".ai" / "workspace" / "debug-report.md"
        if not debug.is_file() or debug.stat().st_size == 0:
            raise WorkflowError(
                "debugger must run first (debug-report.md missing). "
                "Use: engineering-agent bug --invoke --step debugger"
            )


def run_workflow_prepare(
    *,
    root: Path,
    workflow_id: str,
    step: str | None = None,
    run_all: bool = False,
) -> WorkflowRunSummary:
    spec = WORKFLOWS.get(workflow_id)
    if spec is None:
        raise WorkflowError(f"Unknown workflow: {workflow_id}")

    steps = _resolve_steps(spec, step, run_all)
    prepared: list[PrepareResult] = []
    for agent_id in steps:
        prepared.append(run_prepare(root=root, agent_id=agent_id))
    return WorkflowRunSummary(workflow_id=workflow_id, prepared=tuple(prepared), invoked=())


def run_workflow_invoke(
    *,
    root: Path,
    workflow_id: str,
    step: str | None = None,
    run_all: bool = False,
    force: bool = False,
    assume_approved: bool = False,
    git_base: str | None = None,
    git_head: str | None = None,
    with_tests: bool = False,
) -> WorkflowRunSummary:
    spec = WORKFLOWS.get(workflow_id)
    if spec is None:
        raise WorkflowError(f"Unknown workflow: {workflow_id}")

    ctx = load_eas_context(root)
    session = begin_session(root, project_name=ctx.config.project_name)
    steps = _resolve_steps(spec, step, run_all)
    invoked: list[InvokeResult] = []

    with task_scope(session, kind=f"workflow:{workflow_id}", title=workflow_id):
        for agent_id in steps:
            _gate_approval(spec, agent_id, root, assume_approved)
            config = load_eas_context(root).config
            extras = _extra_sections_for_agent(
                root,
                agent_id,
                config=config,
                git_base=git_base,
                git_head=git_head,
                with_tests=with_tests,
            )
            try:
                result = run_invoke(
                    root=root,
                    agent_id=agent_id,
                    force=force,
                    extra_sections=extras,
                )
            except InvokeError as exc:
                raise WorkflowError(str(exc)) from exc
            invoked.append(result)

    return WorkflowRunSummary(workflow_id=workflow_id, prepared=(), invoked=tuple(invoked))


def ensure_project_yaml(root: Path) -> None:
    paths = workspace_paths(root)
    if not paths.project_yaml.is_file():
        raise WorkflowError(
            f"Missing {paths.project_yaml.relative_to(root)} — run engineering-agent init"
        )
    try:
        load_project_config(paths.project_yaml)
    except ProjectConfigError as exc:
        raise WorkflowError(str(exc)) from exc


def ensure_requirement(root: Path) -> None:
    path = root / ".ai" / "workspace" / "requirement.md"
    if not path.is_file() or path.stat().st_size < 20:
        raise WorkflowError(
            "Missing .ai/workspace/requirement.md — fill it before feature workflow"
        )


def resolve_root(start: Path) -> Path:
    return find_repo_root(start)
