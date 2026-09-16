# Engineering Agent System (EAS)

Agentes e workflows vivem em `.ai/` como Markdown. A **CLI** detecta o contexto do projeto (`init`), carrega metadados (`analyze`) e prepara análises — por padrão **não** substitui o host (Cursor, Claude Code, etc.) nem o papel do agente Architect.

## Requisitos

- Python 3.11+

Em **Debian / Ubuntu / WSL**, o Python do sistema costuma não trazer `venv` e `pip`. Use **uma** das opções abaixo.

### Opção A — pacotes do sistema (apt)

```bash
sudo apt update
sudo apt install python3.12-venv python3-pip
```

Depois crie o ambiente virtual e instale:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Opção B — uv (sem apt; recomendado em WSL mínimo)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

Na raiz do repositório:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Ou sem ativar o venv:

```bash
uv run pytest
uv run engineering-agent analyze
```

## Instalação (com o venv pronto)

```bash
pip install -e ".[dev]"
```

Se você já usou `uv pip install` acima, este passo já está feito.

## Uso

Na raiz do repositório (ou em qualquer subpasta de um repo que contenha `.ai/`):

```bash
engineering-agent init                      # detecta stack → .ai/project.yaml
engineering-agent init --dry-run            # só pré-visualiza a detecção
engineering-agent init --force              # sobrescreve project.yaml existente
engineering-agent analyze
engineering-agent analyze --agent architect --prepare   # Phase 2: bundle em .ai/workspace/runs/
engineering-agent analyze --agent architect --invoke    # Phase 2: LLM → artefato (ver abaixo)
engineering-agent analyze --agent documenter --prepare  # documentação / ADRs (isolado)
engineering-agent analyze --path /path/to/repo
engineering-agent analyze --write-draft     # architecture.md mínimo se não existir
engineering-agent --version
```

**Phase 2 (`--invoke`):** exige `pip install -e ".[llm]"` e `ANTHROPIC_API_KEY`. Modelo opcional: `EAS_ANTHROPIC_MODEL`.

**Skill — construir agentes:** [`.ai/skills/agent-builder/SKILL.md`](.ai/skills/agent-builder/SKILL.md) (templates, checklist; agentes com tools, limites e avaliação).

### Agentes principais

| Agente | Artefato em `.ai/workspace/` | Papel resumido |
|--------|------------------------------|----------------|
| Architect | `architecture.md` | Proposta técnica a partir do requisito |
| Tester | `test-plan.md` | Estratégia de testes |
| Reviewer | `code-review.md` | Revisão do diff |
| Documenter | `documentation-report.md` | Docs em `docs/`, ADRs em `docs/adr/` |
| Debugger / Fixer | `debug-report.md`, `fix-plan.md` | Investigação e plano de correção |

Contratos: [`.ai/agents/`](.ai/agents/). Prompts canônicos: [`.ai/hosts/prompts.md`](.ai/hosts/prompts.md).

**Phase 8 (armazenamento de contexto):**

```bash
engineering-agent context status
engineering-agent memory add "Este projeto usa Zod para validação"
engineering-agent context search zod
```

Estado persistente em `.eas/eas.db` (ver [`.ai/PHASE-8.md`](.ai/PHASE-8.md)).

**Phase 7 (limites por papel):**

```bash
engineering-agent agent show architect
engineering-agent agent show documenter
engineering-agent tools --agent architect list
engineering-agent tools --agent architect write-artifact --content "# ..."
```

A política de tools é aplicada no código quando `--agent` está definido (ver [`.ai/PHASE-7.md`](.ai/PHASE-7.md)).

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

**Phase 4 (workflows):** exige `[llm]` + `ANTHROPIC_API_KEY` para `--invoke`.

```bash
engineering-agent feature --prepare --step architect
engineering-agent feature --invoke --step architect --force
engineering-agent feature --invoke --all --assume-approved --force
engineering-agent feature --invoke --step documenter --assume-approved --force
engineering-agent review --invoke --force --git-base main --git-head HEAD
engineering-agent review --invoke --all --force --git-base main --git-head HEAD
engineering-agent bug "detalhes do erro" --invoke --step debugger --force
engineering-agent status
```

Fluxos na CLI: **feature** e **bug** terminam com `documenter` após o reviewer; **review** pode rodar reviewer + documenter com `--all`. Detalhes em [`.ai/PHASE-4.md`](.ai/PHASE-4.md) e [`.ai/workflows/feature.md`](.ai/workflows/feature.md).

**Phase 5 (loop autônomo):**

```bash
engineering-agent loop
engineering-agent loop --invoke-agents --suggest-fix --force
```

Limites em `.ai/project.yaml` → `limits:`. Ver [`.ai/PHASE-5.md`](.ai/PHASE-5.md).

**Phase 6 (integrações):**

```bash
engineering-agent integrations status
engineering-agent integrations github
engineering-agent integrations docker
engineering-agent integrations aws
engineering-agent integrations ci
```

Config opcional: `integrations:` em `.ai/project.yaml`. Ver [`.ai/PHASE-6.md`](.ai/PHASE-6.md).

### Saída do `analyze`

Texto em **pt-BR**: `Análise EAS`, `Projeto`, `Propósito`, `Stack técnica`, `Contexto carregado`, `Workspace EAS`, `Próximos passos`, `Rascunho de arquitetura`. O propósito usa `project.description`, README, manifests e `requirement.md` (seções Problema / História de usuário / Resumo — sem LLM).

Runtime Phase 2: [`.ai/PHASE-2.md`](.ai/PHASE-2.md). Fallback manual no IDE: [`.ai/hosts/prompts.md`](.ai/hosts/prompts.md).

## Contexto do projeto

A CLI lê [`.ai/project.yaml`](.ai/project.yaml) quando o arquivo existe. Os campos seguem [docs/contexto-do-projeto.md](docs/contexto-do-projeto.md) (`project`, `language`, `framework`, `package_manager`, `database`, `testing`, `build`).

Se o arquivo não existir, rode `engineering-agent init` ou a CLI retorna código **2**.

O `init` detecta a stack pelos manifests na raiz:

| Manifest | Stack |
|----------|--------|
| `pyproject.toml` | Python |
| `package.json` | Node / TypeScript |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle(.kts)` | Java / Kotlin (Maven / Gradle) |

**Monorepo (1.1):** vários manifests na raiz **mesclam sinais** na saída; a stack **primária** em `project.yaml` segue prioridade (Python → Node → Go → Rust → Java). Metadados opcionais: `detection.monorepo` e `detection.manifests`.

Também detecta Git, Docker e bancos a partir de `docker-compose.yml`.

## Códigos de saída

| Código | Significado |
|--------|-------------|
| 0 | Sucesso |
| 1 | Erro inesperado (ex.: YAML inválido no `analyze`) |
| 2 | `.ai/project.yaml` ausente (`analyze`) |
| 3 | `.ai/project.yaml` já existe (`init` sem `--force`) |
| 4 | Falha em prepare/invoke do agente (agente ausente, artefato já existe, sem API key, etc.) |
| 5 | Falha em comando `tools` |
| 6 | Falha em workflow (`feature` / `review` / `bug`) |
| 7 | Loop terminou sem sucesso (`loop`) |
| 8 | Falha em CLI/tool de integração (`integrations`, tools `github_*` / `docker_*` / `aws_*` / `ci_*`) |

## Testes

```bash
pytest
```

## Documentação

- [doc.md](doc.md) — índice da documentação do produto
- [.ai/README.md](.ai/README.md) — layout do workspace EAS
- [docs/adr/README.md](docs/adr/README.md) — ADRs (Architecture Decision Records)
- [`.ai/rules/documentation.md`](.ai/rules/documentation.md) — convenções para o agente Documenter
