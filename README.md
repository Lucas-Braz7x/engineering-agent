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
engineering-agent analyze --agent architect --prepare   # Phase 2: bundle em .ai/workspace/runs/
engineering-agent analyze --agent architect --invoke    # Phase 2: LLM → artefato (ver abaixo)
engineering-agent analyze --agent documenter --prepare  # documentação / ADRs (standalone)
engineering-agent analyze --path /path/to/repo
engineering-agent analyze --write-draft     # minimal architecture.md if missing
engineering-agent --version
```

**Phase 2 (`--invoke`):** requer `pip install -e ".[llm]"` e `ANTHROPIC_API_KEY`. Modelo opcional: `EAS_ANTHROPIC_MODEL`.

**Skill — construir agentes:** [`.ai/skills/agent-builder/SKILL.md`](.ai/skills/agent-builder/SKILL.md) (templates + checklist; agentes como sistema com tools, limites e avaliação).

**Phase 8 (context store):**

```bash
engineering-agent context status
engineering-agent memory add "This project uses Zod for validation"
engineering-agent context search zod
```

Persistent state in `.eas/eas.db` (see [`.ai/PHASE-8.md`](.ai/PHASE-8.md)).

**Phase 7 (role boundaries):**

```bash
engineering-agent agent show architect
engineering-agent tools --agent architect list
engineering-agent tools --agent architect write-artifact --content "# ..."
```

Tool policy is enforced in code when `--agent` is set (see [`.ai/PHASE-7.md`](.ai/PHASE-7.md)).

**Phase 3 (tools):**

```bash
engineering-agent tools list
engineering-agent tools read-file README.md
engineering-agent tools search-code 'def analyze' --glob '**/*.py'
engineering-agent tools git-status
engineering-agent tools git-diff --base main --head HEAD
engineering-agent tools run-tests
engineering-agent tools run "pytest -q"
```

Ver [`.ai/PHASE-3.md`](.ai/PHASE-3.md).

**Phase 4 (workflows):** requer `[llm]` + `ANTHROPIC_API_KEY` para `--invoke`.

```bash
engineering-agent feature --prepare --step architect
engineering-agent feature --invoke --step architect --force
engineering-agent feature --invoke --all --assume-approved --force
engineering-agent review --invoke --force --git-base main --git-head HEAD
engineering-agent bug "error details" --invoke --step debugger --force
engineering-agent status
```

Ver [`.ai/PHASE-4.md`](.ai/PHASE-4.md).

**Phase 5 (autonomous loop):**

```bash
engineering-agent loop
engineering-agent loop --invoke-agents --suggest-fix --force
```

Limites em `.ai/project.yaml` → `limits:`. Ver [`.ai/PHASE-5.md`](.ai/PHASE-5.md).

**Phase 6 (integrations):**

```bash
engineering-agent integrations status
engineering-agent integrations github
engineering-agent integrations docker
engineering-agent integrations aws
engineering-agent integrations ci
```

Config opcional: `integrations:` em `.ai/project.yaml`. Ver [`.ai/PHASE-6.md`](.ai/PHASE-6.md).

Saída do `analyze` (em pt-BR): `Análise EAS`, `Projeto`, `Propósito`, `Stack técnica`, `Contexto carregado`, `Workspace EAS`, `Próximos passos`, `Rascunho de arquitetura`. O propósito usa `project.description`, README, manifests e `requirement.md` (seções Problema / História de usuário / Resumo — sem LLM).

Phase 2 runtime: [`.ai/PHASE-2.md`](.ai/PHASE-2.md). Manual host fallback: [`.ai/hosts/prompts.md`](.ai/hosts/prompts.md).

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
| 4 | Agent prepare/invoke failed (missing agent, artifact exists, no API key, etc.) |
| 5 | Tool command failed (`tools` subcommands) |
| 6 | Workflow failed (`feature` / `review` / `bug`) |
| 7 | Loop ended without success (`loop`) |
| 8 | Integration CLI/tool failed (`integrations`, tools `github_*` / `docker_*` / `aws_*` / `ci_*`) |

## Tests

```bash
pytest
```

## Docs

- [doc.md](doc.md) — product documentation index
- [.ai/README.md](.ai/README.md) — EAS workspace layout
