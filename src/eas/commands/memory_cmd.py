from __future__ import annotations

from pathlib import Path

import typer

from eas.context.paths import find_repo_root
from eas.store.connection import ensure_store
from eas.store.repository import (
    add_memory,
    delete_memory,
    ensure_project,
    list_memories,
    update_memory_state,
)

memory_app = typer.Typer(
    help="Curated project memories (.eas/eas.db).",
    no_args_is_help=True,
)

EXIT_OK = 0
EXIT_ERROR = 1


@memory_app.command("list")
def memory_list(
    state: str | None = typer.Option(None, "--state", help="active|candidate|rejected"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            rows = list_memories(store, pid, state=state)
        for row in rows:
            typer.echo(f"{row['id']}\t{row['state']}\t{row['content'][:120]}")
    finally:
        store.close()


@memory_app.command("add")
def memory_add(
    content: str = typer.Argument(..., help="Memory text"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Add an active memory (injected on future prepares)."""
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            mid = add_memory(
                store,
                pid,
                content=content,
                state="active",
                confidence=1.0,
                source_kind="manual",
                source_ref="cli",
            )
        typer.echo(f"Created active memory id={mid}")
    finally:
        store.close()


@memory_app.command("candidates")
def memory_candidates(
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            pid = ensure_project(store)
            rows = list_memories(store, pid, state="candidate")
        for row in rows:
            ref = row.get("source_ref") or ""
            typer.echo(f"{row['id']}\t{ref}\t{row['content'][:160]}")
    finally:
        store.close()


@memory_app.command("promote")
def memory_promote(
    memory_id: int = typer.Argument(..., help="Memory id"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            update_memory_state(store, memory_id, "active")
        typer.echo(f"Promoted memory {memory_id} to active.")
    finally:
        store.close()


@memory_app.command("reject")
def memory_reject(
    memory_id: int = typer.Argument(..., help="Memory id"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            update_memory_state(store, memory_id, "rejected")
        typer.echo(f"Rejected memory {memory_id}.")
    finally:
        store.close()


@memory_app.command("forget")
def memory_forget(
    memory_id: int = typer.Argument(..., help="Memory id"),
    path: Path = typer.Option(Path("."), "--path", exists=True, file_okay=False, dir_okay=True),
) -> None:
    root = find_repo_root(path)
    store = ensure_store(root)
    try:
        with store.transaction():
            delete_memory(store, memory_id)
        typer.echo(f"Deleted memory {memory_id}.")
    finally:
        store.close()
