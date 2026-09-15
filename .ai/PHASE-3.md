# Phase 3 — Tools

Critério do [roadmap](../docs/roadmap.md): filesystem, shell, git, tests — API estável para agentes e CLI.

## Módulos

| Tool | Módulo | CLI |
|------|--------|-----|
| `read_file` | `eas/tools/filesystem.py` | `tools read-file` |
| `write_file` | `eas/tools/filesystem.py` | `tools write-file --content` |
| `write_artifact` | `eas/tools/filesystem.py` | `tools --agent <id> write-artifact --content` |
| `search_code` | `eas/tools/filesystem.py` | `tools search-code` |
| `run_command` | `eas/tools/shell.py` | `tools run` |
| `run_tests` | `eas/tools/tests_tool.py` | `tools run-tests` |
| `git_diff` | `eas/tools/git_tools.py` | `tools git-diff` |
| `git_status` | `eas/tools/git_tools.py` | `tools git-status` |
| `git_log` | `eas/tools/git_tools.py` | `tools git-log` |

Programático: `eas.tools.execute(ToolContext, name, agent=manifest, **kwargs)` (Phase 7: `agent` aplica política de role).

## Segurança (MVP)

- Paths resolvidos sob o repo root (`find_repo_root`)
- Escrita bloqueada em `.git/`
- `run_command`: sem shell, timeout 120s, blocklist (`rm`, `sudo`, …)
- Saída truncada em ~256KB

## Integração

- `analyze --agent … --prepare` inclui catálogo de tools no `invoke.md`
- Phase 4: workflows/agent loop chamarão `execute()` diretamente

## Exit code CLI

| Code | Meaning |
|------|---------|
| 5 | Tool failed (`tools` subcommands) |
