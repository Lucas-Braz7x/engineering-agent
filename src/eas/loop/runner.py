from __future__ import annotations

from pathlib import Path

from eas.context.loader import ProjectConfig
from eas.loop.budget import LoopBlockedError, LoopBudget
from eas.context.limits import LoopLimits
from eas.loop.report import LoopOutcome, write_loop_report
from eas.runtime.invoke import InvokeError, run_invoke
from eas.runtime.load_context import load_eas_context
from eas.tools.models import ToolContext
from eas.tools.registry import execute
from eas.workflows.context_bundle import gather_git_context
from eas.store.recording import begin_session, task_scope


def _limits_for_config(config: ProjectConfig) -> LoopLimits:
    if config.limits is not None:
        return config.limits
    return LoopLimits()


def _invoke_agent(
    root: Path,
    agent_id: str,
    budget: LoopBudget,
    config: ProjectConfig,
    *,
    force: bool,
    extra_sections: tuple[tuple[str, str], ...],
) -> None:
    budget.record_agent()
    run_invoke(
        root=root,
        agent_id=agent_id,
        force=force,
        extra_sections=extra_sections,
    )


def run_autonomous_loop(
    root: Path,
    *,
    invoke_agents: bool,
    suggest_fix: bool,
    review_on_success: bool,
    force: bool,
    limits_override: LoopLimits | None = None,
) -> LoopOutcome:
    context = load_eas_context(root)
    session = begin_session(root, project_name=context.config.project_name)
    limits = limits_override or _limits_for_config(context.config)
    budget = LoopBudget(limits=limits)
    tool_ctx = ToolContext(root=root, config=context.config)

    last_exit: int | None = None
    reason = ""

    try:
        with task_scope(session, kind="loop", title="autonomous-loop"):
            outcome = _loop_body(
                root=root,
                context=context,
                budget=budget,
                tool_ctx=tool_ctx,
                invoke_agents=invoke_agents,
                suggest_fix=suggest_fix,
                review_on_success=review_on_success,
                force=force,
            )
            write_loop_report(root, outcome)
            return outcome
    except LoopBlockedError as exc:
        outcome = LoopOutcome(
            status="WORKFLOW_BLOCKED",
            reason=exc.reason,
            budget=budget,
            last_test_exit_code=last_exit,
        )
        write_loop_report(root, outcome)
        return outcome


def _loop_body(
    *,
    root: Path,
    context,
    budget: LoopBudget,
    tool_ctx: ToolContext,
    invoke_agents: bool,
    suggest_fix: bool,
    review_on_success: bool,
    force: bool,
) -> LoopOutcome:
    last_exit: int | None = None
    reason = ""
    try:
        while True:
            budget.begin_iteration()

            test_result = execute(tool_ctx, "run_tests")
            budget.record_command()
            last_exit = test_result.exit_code

            if test_result.ok:
                reason = "All tests passed."
                if review_on_success and invoke_agents:
                    extras = tuple(
                        gather_git_context(
                            root,
                            context.config,
                            git_base=None,
                            git_head=None,
                            include_tests=False,
                        )
                    )
                    _invoke_agent(
                        root,
                        "reviewer",
                        budget,
                        context.config,
                        force=force,
                        extra_sections=extras,
                    )
                outcome = LoopOutcome(
                    status="SUCCESS",
                    reason=reason,
                    budget=budget,
                    last_test_exit_code=last_exit,
                )
                return outcome

            reason = test_result.error or "Tests failed."
            test_body = test_result.output or reason
            extras: tuple[tuple[str, str], ...] = (("Test failure output", test_body),)

            if not invoke_agents:
                outcome = LoopOutcome(
                    status="TESTS_FAILED",
                    reason="Tests failed; re-run with --invoke-agents to call debugger.",
                    budget=budget,
                    last_test_exit_code=last_exit,
                )
                return outcome

            extras = extras + tuple(
                gather_git_context(
                    root,
                    context.config,
                    git_base=None,
                    git_head=None,
                    include_tests=False,
                )
            )

            try:
                _invoke_agent(
                    root,
                    "debugger",
                    budget,
                    context.config,
                    force=force,
                    extra_sections=extras,
                )
                if suggest_fix:
                    debug_path = root / ".ai/workspace/debug-report.md"
                    debug_text = (
                        debug_path.read_text(encoding="utf-8")
                        if debug_path.is_file()
                        else "(no debug report)"
                    )
                    fix_extras = extras + (("debug-report.md", debug_text),)
                    _invoke_agent(
                        root,
                        "fixer",
                        budget,
                        context.config,
                        force=force,
                        extra_sections=fix_extras,
                    )
            except InvokeError as exc:
                outcome = LoopOutcome(
                    status="WORKFLOW_BLOCKED",
                    reason=str(exc),
                    budget=budget,
                    last_test_exit_code=last_exit,
                )
                return outcome

            # Next loop iteration re-runs tests (human or fixer plan may have changed files externally)

    except LoopBlockedError as exc:
        return LoopOutcome(
            status="WORKFLOW_BLOCKED",
            reason=exc.reason,
            budget=budget,
            last_test_exit_code=last_exit,
        )
