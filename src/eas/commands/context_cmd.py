from __future__ import annotations

from pathlib import Path

import typer

from eas.context.paths import find_repo_root
from eas.store.connection import StoreError, ensure_store, is_context_enabled
from eas.store.repository import count_rows, ensure_project, list_recent_runs
from eas.store.retention import apply_prune, plan_prune, policy_from_dict, vacuum_db
from eas.store.search import search_context

context_app = typer.Typer(
    help="Persistent context store (.eas/eas.db).",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_ERROR = 1


def _policy_for_root(root: Path):
    import yaml

    path = root / ".ai" / "project.yaml"
    if not path.is_file():
        return policy_from_dict(None)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("context"), dict):
            ret = data["context"].get("retention")
            if isinstance(ret, dict):
                return policy_from_dict(ret)
    except Exception:
        pass
    return policy_from_dict(None)


@context_app.command("status")
def context_status(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Show store path, row counts, and FTS availability."""
    root = find_repo_root(path)
    if not is_context_enabled(root):
        typer.echo("Context store disabled (EAS_CONTEXT=0).")
        raise typer.Exit(EXIT_OK)
    try:
        store = ensure_store(root)
    except StoreError as exc:
        typer.secho(str(exc), err=True)
        raise typer.Exit(EXIT_ERROR)
    try:
        with store.transaction():
            pid = ensure_project(store)
            counts = count_rows(store)
        db = store.db_path
        size = db.stat().st_size if db.is_file() else 0
        typer.echo(f"Store: {db.relative_to(root) if db.is_relative_to(root) else db}")
        typer.echo(f"Size: {size} bytes")
        typer.echo(f"Project id: {pid}")
        for table, count in counts.items():
            typer.echo(f"  {table}: {count}")
    finally:
        store.close()


@context_app.command("search")
def context_search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Search memories and decisions."""
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            hits = search_context(store, pid, query, limit=limit)
        if not hits:
            typer.echo("(no results)")
            return
        for hit in hits:
            typer.echo(f"[{hit['type']}] id={hit.get('id')} {hit.get('snippet', '')}")
    finally:
        store.close()


@context_app.command("history")
def context_history(
    limit: int = typer.Option(20, "--limit"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """List recent agent runs."""
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            runs = list_recent_runs(store, pid, limit=limit)
        for run in runs:
            typer.echo(
                f"{run['created_at']}\t{run['id']}\t{run['agent_id']}\t"
                f"{run['kind']}/{run['status']}"
            )
    finally:
        store.close()


@context_app.command("prune")
def context_prune(
    apply: bool = typer.Option(False, "--apply", help="Apply deletion (default: dry-run)"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Prune old runs/messages and stale memory candidates."""
    root = find_repo_root(path)
    store = ensure_store(root)
    policy = _policy_for_root(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            plan = plan_prune(store, pid, policy)
        typer.echo(f"Runs to delete: {len(plan.runs_to_delete)}")
        typer.echo(f"Messages affected: {plan.messages_to_delete}")
        typer.echo(f"Stale candidates: {len(plan.candidates_to_delete)}")
        if apply and (plan.runs_to_delete or plan.candidates_to_delete):
            with store.transaction():
                apply_prune(store, plan)
            typer.echo("Applied.")
        elif not apply:
            typer.echo("(dry-run — pass --apply to delete)")
    finally:
        store.close()


@context_app.command("vacuum")
def context_vacuum(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Checkpoint WAL and VACUUM the database."""
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        freed = vacuum_db(store)
        store._conn.commit()
        typer.echo(f"Vacuum complete (approx. {freed} bytes reclaimed).")
    finally:
        store.close()
