from __future__ import annotations

from pathlib import Path

import typer

from eas.context.limits import LoopLimits
from eas.loop.runner import run_autonomous_loop
from eas.workflows.runner import WorkflowError, ensure_project_yaml, resolve_root

EXIT_OK = 0
EXIT_LOOP = 7


def loop(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
    invoke_agents: bool = typer.Option(
        False,
        "--invoke-agents",
        help="On test failure, invoke debugger (and optional fixer). Requires LLM.",
    ),
    suggest_fix: bool = typer.Option(
        False,
        "--suggest-fix",
        help="After debugger, invoke fixer → fix-plan.md (requires --invoke-agents).",
    ),
    review_on_success: bool = typer.Option(
        False,
        "--review-on-success",
        help="Invoke reviewer when tests pass (requires --invoke-agents).",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite agent artifacts."),
    max_iterations: int | None = typer.Option(None, "--max-iterations"),
    max_command_execution: int | None = typer.Option(None, "--max-command-execution"),
    max_agent_calls: int | None = typer.Option(None, "--max-agent-calls"),
) -> None:
    """Autonomous loop: test → (fail → debug → fix plan) → retry until green or limits (Phase 5)."""
    root = resolve_root(path)
    try:
        ensure_project_yaml(root)
    except WorkflowError as exc:
        typer.secho(str(exc), err=True)
        raise typer.Exit(EXIT_LOOP)

    override: LoopLimits | None = None
    if any(v is not None for v in (max_iterations, max_command_execution, max_agent_calls)):
        override = LoopLimits(
            max_iterations=max_iterations or 5,
            max_command_execution=max_command_execution or 20,
            max_agent_calls=max_agent_calls or 30,
        )

    outcome = run_autonomous_loop(
        root,
        invoke_agents=invoke_agents,
        suggest_fix=suggest_fix,
        review_on_success=review_on_success,
        force=force,
        limits_override=override,
    )

    typer.echo(f"Loop status: {outcome.status}")
    typer.echo(outcome.reason)
    typer.echo(
        f"Budget: iterations={outcome.budget.iterations} "
        f"commands={outcome.budget.command_executions} "
        f"agents={outcome.budget.agent_calls}"
    )
    typer.echo("Report: .ai/workspace/loop-report.md")

    if outcome.status == "SUCCESS":
        raise typer.Exit(EXIT_OK)
    raise typer.Exit(EXIT_LOOP)
