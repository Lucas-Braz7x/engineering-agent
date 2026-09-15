from __future__ import annotations

from pathlib import Path

import typer

from eas import __version__
from eas.analysis.draft import write_minimal_draft
from eas.analysis.report import build_report
from eas.context.loader import ProjectConfigError, load_project_config
from eas.context.paths import find_repo_root, workspace_paths
from eas.runtime.invoke import (
    InvokeError,
    format_invoke_message,
    format_prepare_message,
    run_invoke,
    run_prepare,
)
from eas.runtime.load_context import load_eas_context
from eas.runtime.load_agent import AgentLoadError

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_MISSING_CONFIG = 2
EXIT_AGENT_ERROR = 4


def run_analyze(
    *,
    start_path: Path,
    write_draft: bool,
    agent: str | None,
    prepare: bool,
    invoke: bool,
    force: bool,
) -> int:
    root = find_repo_root(start_path)
    paths = workspace_paths(root)

    if not paths.project_yaml.is_file():
        try:
            missing = paths.project_yaml.relative_to(root)
        except ValueError:
            missing = paths.project_yaml
        typer.secho(f"Missing {missing}.", err=True)
        typer.secho(
            "Run 'engineering-agent init' to generate .ai/project.yaml, or create it manually (see docs/contexto-do-projeto.md).",
            err=True,
        )
        return EXIT_MISSING_CONFIG

    try:
        config = load_project_config(paths.project_yaml)
    except ProjectConfigError as exc:
        typer.secho(str(exc), err=True)
        return EXIT_ERROR

    if agent:
        if prepare == invoke:
            typer.secho(
                "Specify exactly one of --prepare or --invoke when using --agent.",
                err=True,
            )
            return EXIT_ERROR
        try:
            if prepare:
                result = run_prepare(root=root, agent_id=agent)
                typer.echo(format_prepare_message(result, root), nl=False)
                return EXIT_OK
            result = run_invoke(root=root, agent_id=agent, force=force)
            typer.echo(format_invoke_message(result, root), nl=False)
            return EXIT_OK
        except (InvokeError, AgentLoadError) as exc:
            typer.secho(str(exc), err=True)
            return EXIT_AGENT_ERROR

    context = load_eas_context(root, config=config)

    if write_draft:
        draft_status = write_minimal_draft(paths)
    else:
        draft_status = "not requested"

    report = build_report(
        version=__version__,
        config=config,
        paths=paths,
        draft_status=draft_status,
        rules_count=len(context.rules),
        skills_count=len(context.skills),
        has_requirement=context.requirement_text is not None,
    )
    typer.echo(report, nl=False)
    return EXIT_OK


def analyze(
    path: Path = typer.Option(
        Path("."),
        "--path",
        help="Project directory (repo root or subdirectory).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    write_draft: bool = typer.Option(
        False,
        "--write-draft",
        help="Create a minimal .ai/workspace/architecture.md if it does not exist.",
    ),
    agent: str | None = typer.Option(
        None,
        "--agent",
        help="EAS agent to run: architect, tester, reviewer, or debugger.",
    ),
    prepare: bool = typer.Option(
        False,
        "--prepare",
        help="Write invoke bundle under .ai/workspace/runs/ (requires --agent).",
    ),
    invoke: bool = typer.Option(
        False,
        "--invoke",
        help="Call Anthropic and write agent artifact (requires --agent).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing artifact when using --invoke.",
    ),
) -> None:
    code = run_analyze(
        start_path=path,
        write_draft=write_draft,
        agent=agent,
        prepare=prepare,
        invoke=invoke,
        force=force,
    )
    if code != EXIT_OK:
        raise typer.Exit(code=code)
