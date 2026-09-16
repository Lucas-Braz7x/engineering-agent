from __future__ import annotations

from pathlib import Path

import typer

from eas.runtime.invoke import format_invoke_message, format_prepare_message
from eas.workflows.context_bundle import write_bug_report
from eas.workflows.runner import (
    WorkflowError,
    ensure_project_yaml,
    ensure_requirement,
    resolve_root,
    run_workflow_invoke,
    run_workflow_prepare,
)

EXIT_OK = 0
EXIT_WORKFLOW = 6


def _common_options(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
    prepare: bool = typer.Option(False, "--prepare"),
    invoke: bool = typer.Option(False, "--invoke"),
    step: str | None = typer.Option(
        None,
        "--step",
        help="Agent step: architect, tester, reviewer, documenter, debugger",
    ),
    all_steps: bool = typer.Option(False, "--all", help="All workflow steps"),
    force: bool = typer.Option(False, "--force"),
    assume_approved: bool = typer.Option(
        False,
        "--assume-approved",
        help="Skip architecture approval gate (feature) or post-debug gate (bug)",
    ),
    git_base: str | None = typer.Option(None, "--git-base"),
    git_head: str | None = typer.Option(None, "--git-head"),
    with_tests: bool = typer.Option(False, "--with-tests", help="Attach test output for reviewer"),
) -> dict:
    return {
        "path": path,
        "prepare": prepare,
        "invoke": invoke,
        "step": step,
        "all_steps": all_steps,
        "force": force,
        "assume_approved": assume_approved,
        "git_base": git_base,
        "git_head": git_head,
        "with_tests": with_tests,
    }


def _run_workflow_cli(workflow_id: str, opts: dict) -> int:
    if opts["prepare"] == opts["invoke"]:
        typer.secho("Specify exactly one of --prepare or --invoke.", err=True)
        return 1

    root = resolve_root(opts["path"])
    try:
        ensure_project_yaml(root)
    except WorkflowError as exc:
        typer.secho(str(exc), err=True)
        return EXIT_WORKFLOW

    try:
        if opts["prepare"]:
            summary = run_workflow_prepare(
                root=root,
                workflow_id=workflow_id,
                step=opts["step"],
                run_all=opts["all_steps"],
            )
            for item in summary.prepared:
                typer.echo(format_prepare_message(item, root), nl=False)
            return EXIT_OK

        summary = run_workflow_invoke(
            root=root,
            workflow_id=workflow_id,
            step=opts["step"],
            run_all=opts["all_steps"],
            force=opts["force"],
            assume_approved=opts["assume_approved"],
            git_base=opts["git_base"],
            git_head=opts["git_head"],
            with_tests=opts["with_tests"],
        )
        for item in summary.invoked:
            typer.echo(format_invoke_message(item, root), nl=False)
        return EXIT_OK
    except WorkflowError as exc:
        typer.secho(str(exc), err=True)
        return EXIT_WORKFLOW


def feature(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
    prepare: bool = typer.Option(False, "--prepare"),
    invoke: bool = typer.Option(False, "--invoke"),
    step: str | None = typer.Option(None, "--step"),
    all_steps: bool = typer.Option(False, "--all"),
    force: bool = typer.Option(False, "--force"),
    assume_approved: bool = typer.Option(False, "--assume-approved"),
    git_base: str | None = typer.Option(None, "--git-base"),
    git_head: str | None = typer.Option(None, "--git-head"),
    with_tests: bool = typer.Option(False, "--with-tests"),
    requirement: str | None = typer.Option(
        None,
        "-m",
        "--message",
        help="Optional short requirement title (does not replace requirement.md)",
    ),
) -> None:
    """Feature workflow: architect → tester → reviewer → documenter (see .ai/workflows/feature.md)."""
    root = resolve_root(path)
    if requirement:
        req_path = root / ".ai" / "workspace" / "requirement.md"
        if not req_path.is_file():
            req_path.parent.mkdir(parents=True, exist_ok=True)
            req_path.write_text(
                f"# Requirement\n\n## Title\n\n{requirement}\n",
                encoding="utf-8",
            )
    try:
        ensure_requirement(root)
    except WorkflowError as exc:
        typer.secho(str(exc), err=True)
        raise typer.Exit(EXIT_WORKFLOW)

    opts = _common_options(
        path=path,
        prepare=prepare,
        invoke=invoke,
        step=step,
        all_steps=all_steps,
        force=force,
        assume_approved=assume_approved,
        git_base=git_base,
        git_head=git_head,
        with_tests=with_tests,
    )
    raise typer.Exit(_run_workflow_cli("feature", opts))


def review(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
    prepare: bool = typer.Option(False, "--prepare"),
    invoke: bool = typer.Option(False, "--invoke"),
    step: str | None = typer.Option(None, "--step"),
    all_steps: bool = typer.Option(False, "--all", help="Reviewer and documenter"),
    force: bool = typer.Option(False, "--force"),
    git_base: str | None = typer.Option("main", "--git-base"),
    git_head: str | None = typer.Option("HEAD", "--git-head"),
    with_tests: bool = typer.Option(False, "--with-tests"),
) -> None:
    """Review workflow: reviewer → documenter with git diff context."""
    opts = _common_options(
        path=path,
        prepare=prepare,
        invoke=invoke,
        step=step,
        all_steps=all_steps,
        force=force,
        git_base=git_base,
        git_head=git_head,
        with_tests=with_tests,
    )
    raise typer.Exit(_run_workflow_cli("review", opts))


def bug(
    description: str | None = typer.Argument(None, help="Bug summary / stack trace"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
    prepare: bool = typer.Option(False, "--prepare"),
    invoke: bool = typer.Option(False, "--invoke"),
    step: str | None = typer.Option(None, "--step"),
    all_steps: bool = typer.Option(False, "--all"),
    force: bool = typer.Option(False, "--force"),
    assume_approved: bool = typer.Option(
        False,
        "--assume-approved",
        help="After you applied a fix, run tester+reviewer without re-checking debug-report",
    ),
    git_base: str | None = typer.Option(None, "--git-base"),
    git_head: str | None = typer.Option(None, "--git-head"),
    with_tests: bool = typer.Option(False, "--with-tests"),
) -> None:
    """Bug workflow: debugger → tester → reviewer → documenter."""
    root = resolve_root(path)
    if description:
        write_bug_report(root, description)

    opts = _common_options(
        path=path,
        prepare=prepare,
        invoke=invoke,
        step=step,
        all_steps=all_steps,
        force=force,
        assume_approved=assume_approved,
        git_base=git_base,
        git_head=git_head,
        with_tests=with_tests,
    )
    raise typer.Exit(_run_workflow_cli("bug", opts))


def status(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Show workspace artifacts and recent runs."""
    root = resolve_root(path)
    ws = root / ".ai" / "workspace"
    typer.echo("EAS workspace status\n")
    artifacts = [
        "requirement.md",
        "architecture.md",
        "approval.md",
        "test-plan.md",
        "code-review.md",
        "documentation-report.md",
        "debug-report.md",
        "bug-report.md",
        "fix-plan.md",
        "loop-report.md",
    ]
    for name in artifacts:
        p = ws / name
        if p.is_file():
            typer.echo(f"  ✓ {name} ({p.stat().st_size} bytes)")
        else:
            typer.echo(f"  · {name} (missing)")

    runs = ws / "runs"
    if runs.is_dir():
        children = sorted(runs.iterdir(), key=lambda p: p.name, reverse=True)[:5]
        if children:
            typer.echo("\nRecent runs:")
            for run_dir in children:
                typer.echo(f"  - {run_dir.name}")
