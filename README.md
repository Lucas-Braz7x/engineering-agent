# Engineering Agent System

Agents and workflows live in `.ai/` as Markdown. The **CLI** detects project context (`init`), loads it (`analyze`), and prepares analysis — it does **not** call an LLM or replace the architect agent.

## Requirements

- Python 3.11+

On **Debian / Ubuntu / WSL**, the system Python often lacks `venv` and `pip`. Use **one** of the options below.

### Option A — system packages (apt)

```bash
sudo apt update
sudo apt install python3.12-venv python3-pip
```

Then create a virtualenv and install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Option B — uv (no apt; recommended on minimal WSL)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

From the repo root:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Or without activating the venv:

```bash
uv run pytest
uv run engineering-agent analyze
```

## Install (after venv is ready)

```bash
pip install -e ".[dev]"
```

If you used `uv pip install` above, this step is already done.

## Usage

From the repository root (or any subdirectory under a repo that contains `.ai/`):

```bash
engineering-agent init                      # detect stack → .ai/project.yaml
engineering-agent init --dry-run            # preview detection only
engineering-agent init --force              # overwrite existing project.yaml
engineering-agent analyze
engineering-agent analyze --path /path/to/repo
engineering-agent analyze --write-draft     # minimal architecture.md if missing
engineering-agent --version
```

Example output sections: `EAS analyze`, `Project`, `Stack`, `Workspace`, `Recommendation`, `Draft`.

To produce a full architecture document, invoke the **architect** agent in Cursor or Claude Code using [`.ai/hosts/prompts.md`](.ai/hosts/prompts.md).

## Project context

The CLI reads [`.ai/project.yaml`](.ai/project.yaml) when present. Supported fields mirror [docs/contexto-do-projeto.md](docs/contexto-do-projeto.md) (`project`, `language`, `framework`, `package_manager`, `database`, `testing`, `build`).

If the file is missing, run `engineering-agent init` or exit code **2**.

`init` detects stack from root manifests:

| Manifest | Stack |
|----------|--------|
| `pyproject.toml` | Python |
| `package.json` | Node / TypeScript |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle(.kts)` | Java / Kotlin (Maven / Gradle) |

**Monorepo (1.1):** multiple manifests at the repo root merge **signals** in the output; the **primary** stack in `project.yaml` follows priority (Python → Node → Go → Rust → Java). Optional metadata: `detection.monorepo` and `detection.manifests`.

Also detects Git, Docker, and databases from `docker-compose.yml`.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unexpected error (e.g. invalid YAML on analyze) |
| 2 | Missing `.ai/project.yaml` (`analyze`) |
| 3 | `.ai/project.yaml` already exists (`init` without `--force`) |

## Tests

```bash
pytest
```

## Docs

- [doc.md](doc.md) — product documentation index
- [.ai/README.md](.ai/README.md) — EAS workspace layout
