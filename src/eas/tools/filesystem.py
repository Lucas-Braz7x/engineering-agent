from __future__ import annotations

import re
from pathlib import Path

from eas.tools.errors import ToolError
from eas.tools.models import ToolContext, ToolResult
from eas.tools.policy import (
    assert_artifact_write_path,
    assert_writable,
    resolve_repo_path,
    should_skip_dir,
)

DEFAULT_SEARCH_MAX = 50
MAX_READ_BYTES = 512_000


def read_file(ctx: ToolContext, *, path: str) -> ToolResult:
    try:
        target = resolve_repo_path(ctx.root, path)
    except Exception as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    if not target.is_file():
        return ToolResult(ok=False, output="", error=f"Not a file: {path}")

    size = target.stat().st_size
    if size > MAX_READ_BYTES:
        return ToolResult(
            ok=False,
            output="",
            error=f"File too large ({size} bytes; max {MAX_READ_BYTES})",
        )

    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ToolResult(ok=False, output="", error="File is not valid UTF-8 text")
    except OSError as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    try:
        rel = target.relative_to(ctx.root.resolve())
    except ValueError:
        rel = target
    return ToolResult(ok=True, output=f"=== {rel} ===\n{text}")


def write_file(ctx: ToolContext, *, path: str, content: str) -> ToolResult:
    try:
        target = resolve_repo_path(ctx.root, path)
        assert_writable(target, ctx.root)
    except Exception as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    return ToolResult(ok=True, output=f"Wrote {len(content.encode('utf-8'))} bytes to {path}")


def write_artifact(
    ctx: ToolContext,
    *,
    path: str,
    content: str,
    artifact_path: str,
) -> ToolResult:
    try:
        assert_artifact_write_path(path, artifact_path)
        target = resolve_repo_path(ctx.root, path)
        assert_writable(target, ctx.root)
    except Exception as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return ToolResult(ok=False, output="", error=str(exc))

    return ToolResult(
        ok=True,
        output=f"Wrote artifact ({len(content.encode('utf-8'))} bytes) to {path}",
    )


def search_code(
    ctx: ToolContext,
    *,
    pattern: str,
    glob: str = "**/*",
    max_results: int = DEFAULT_SEARCH_MAX,
) -> ToolResult:
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        return ToolResult(ok=False, output="", error=f"Invalid regex: {exc}")

    root = ctx.root.resolve()
    matches: list[str] = []
    scanned = 0

    for path in root.glob(glob):
        if not path.is_file():
            continue
        if any(should_skip_dir(part) for part in path.relative_to(root).parts):
            continue
        if path.stat().st_size > MAX_READ_BYTES:
            continue

        scanned += 1
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        rel = path.relative_to(root)
        for line_no, line in enumerate(lines, start=1):
            if regex.search(line):
                matches.append(f"{rel}:{line_no}:{line.rstrip()}")
                if len(matches) >= max_results:
                    break
        if len(matches) >= max_results:
            break

    header = f"Pattern: {pattern!r}  glob: {glob!r}  scanned_files: {scanned}\n"
    body = "\n".join(matches) if matches else "(no matches)"
    return ToolResult(ok=True, output=header + body)
