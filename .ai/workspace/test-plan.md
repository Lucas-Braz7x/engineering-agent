# Test plan — CLI `engineering-agent analyze`

## Summary

Plano de testes para o stub `analyze` introduzido nos commits `70a5567` (feat), `6224c53` (README), `ed50088` (project.yaml), `ebc39b4` (uv.lock), sobre a base Phase 0 já commitada em `f6d9a90`. A suíte automatizada cobre **14 testes pytest** (loader, CLI, report, paths). Lacunas must **automatizadas** T7–T9 fechadas em `tests/test_analyze.py`; T10–T13 implementados. **Pendente manual:** M1, M2 (smoke README / sem LLM).

Respostas às perguntas obrigatórias do agente tester:

1. **What changed?** Novo pacote `src/eas/` (CLI Typer, loader, paths, report, draft), entrypoint `engineering-agent`, testes em `tests/`, `.ai/project.yaml` para dogfooding.
2. **What can break?** Resolução de repo root; parse YAML tolerante demais ou falho; exit codes errados; sobrescrita acidental de `architecture.md`; saída stdout instável; mensagem confusa sem `project.yaml`.
3. **What tests already exist?** `test_context_loader.py` (5), `test_analyze.py` (6), `test_report.py` (2), `test_paths.py` (1) — ver *Existing coverage*.
4. **What tests are missing?** Apenas manual M1–M2 e opcional e2e T14 (subprocess binário).
5. **Which edge cases matter?** Subdiretório sem `.ai` local; `project.yaml` ausente vs inválido vs vazio; `--write-draft` com arquivo existente; `requirement.md` ausente ou sem `## Title`.
6. **Unit vs integration?** Unit: `loader`, `paths`, `report`, `draft`. Integration: Typer `CliRunner` (comando completo). E2E/manual: script instalado no PATH e repo EAS real.

## Scope of change

| Área | Arquivos / contrato | Commits |
|------|---------------------|---------|
| CLI público | `engineering-agent`, `analyze [--path] [--write-draft]`, `--version` | `70a5567` |
| Exit codes | 0 OK, 1 erro parse/leitura, 2 sem `project.yaml` | `70a5567` |
| Contexto | `.ai/project.yaml` → `ProjectConfig` | `70a5567`, `ed50088` |
| Saída | Seções `EAS analyze`, `Project`, `Stack`, `Workspace`, `Recommendation`, `Draft` | `70a5567` |
| Draft | `--write-draft` idempotente | `70a5567` |
| Docs / run | README, `testing.command: pytest` | `6224c53`, `ed50088` |

Diff analisado: `bea1761...HEAD` (foco `src/`, `tests/`).

## Risk & failure modes

| Risco (arch.) | Modo de falha | Sinal |
|---------------|---------------|-------|
| Schema informal `project.yaml` | Campos ignorados ou crash | Stack incompleto ou exceção |
| Expectativa analyze = Architect | Usuário acha que LLM roda | Recommendation ausente ou teste manual omitido |
| Sobrescrever `architecture.md` | Perda de artefato agente | Draft sobrescreve arquivo existente |
| `find_repo_root` em monorepo | Path `.ai` errado | analyze lê yaml de outro projeto |
| Exit code CI | Script não distingue missing vs error | Exit 0 com yaml quebrado |
| Saída instável | Quebra smoke/ snapshot | Ordem ou labels de seção mudam |

## Existing coverage

| Teste | Tipo | O que valida | Rastreio |
|-------|------|--------------|----------|
| `test_load_valid_project_yaml` | unit | Parse completo fixture `valid.yaml` | AC loader; F3 |
| `test_load_missing_file` | unit | `ProjectConfigError` se arquivo ausente | loader |
| `test_load_invalid_yaml` | unit | YAML malformado → erro | Risco parse |
| `test_analyze_missing_project_yaml` | integration | exit **2**, stderr Missing + init | AC critério 2; F4; NF3 |
| `test_analyze_success` | integration | exit 0, `EAS analyze`, Recommendation, Draft not requested | F2, F6 parcial |
| `test_analyze_write_draft` | integration | cria draft, idempotência `skipped (exists)` | AC critério 3; F5 |
| `test_find_repo_root_from_subdirectory` | integration | `--path` em subpasta sobe até `.ai/` | F2; paths |
| `test_analyze_invalid_project_yaml_exit_1` | integration | exit **1** com yaml inválido (T7) | NF3, F3 |
| `test_cli_version` | integration | `--version` → `0.1.0` (T10) | F1 |
| `test_load_empty_yaml` / `test_load_non_mapping_root` | unit | `{}` e root lista (T11/T12) | schema |
| `test_build_report_empty_config_stack_placeholder` | unit | placeholder stack (T11) | Q5 |
| `test_build_report_empty_project_yaml_via_analyze` | integration | `{}` no CLI (T11) | Q5 |
| `test_find_repo_root_without_ai_returns_start` | unit | sem `.ai` (T13) | paths |

**Comando verificado:** `pytest` (**14 passed**).

**Não coberto por automatizado:** README/entrypoint documentado (AC 1), `pyproject.toml` deps (AC 4) — verificação estrutural/manual.

## Test gaps

| Gap | Prioridade | Status |
|-----|------------|--------|
| CLI exit 1 / Workspace / Recommendation (T7–T9) | must | **closed** (automated) |
| `--version`, YAML vazio, root lista (T10–T12) | should | **closed** |
| `find_repo_root` sem `.ai` (T13) | could | **closed** |
| Subprocess binário instalado (T14) | could | open |
| Dogfooding README + analyze no repo (M1) | manual must | checklist |
| Sem LLM no analyze (M2) | manual must | checklist |

**gaps_high (must automatizado faltando):** 0

## Proposed test cases

| ID | Tipo | Descrição | Critério / risco | Prioridade | Status |
|----|------|-----------|------------------|------------|--------|
| T1 | unit | Parse fixture `valid.yaml` todos os campos | AC loader | must | **implemented** |
| T2 | unit | Arquivo yaml ausente no loader | loader | must | **implemented** |
| T3 | unit | YAML inválido no loader | parse | must | **implemented** |
| T4 | integration | Sem `project.yaml` → exit 2 + hint init | AC #2, F4 | must | **implemented** |
| T5 | integration | Analyze OK + contrato Workspace/Recommendation | F2, F6, F5 | must | **implemented** |
| T6 | integration | `--write-draft` create + skip exists | AC #3, F5 | must | **implemented** |
| T7 | integration | `.ai/project.yaml` inválido → exit **1** | NF3, F3 | must | **implemented** |
| T8 | integration | paths `architecture.md` / `requirement.md` | AC #3, F5 | must | **implemented** |
| T9 | integration | Recommendation `prompts.md` / `architect.md` | F6 | must | **implemented** |
| T10 | integration | `--version` | F1 | should | **implemented** |
| T11 | unit/integration | YAML vazio → stack placeholder | Q5 | should | **implemented** |
| T12 | unit | YAML root lista → erro | loader | should | **implemented** |
| T13 | unit | `find_repo_root` sem `.ai` | paths | could | **implemented** |
| T14 | e2e | `subprocess` binário instalado na raiz EAS | F1 | could | **missing** |
| M1 | manual | README: venv/uv + `engineering-agent analyze` no repo | AC #1, #4 | must | **checklist** |
| M2 | manual | Confirmar que analyze **não** chama LLM | constraint | must | **checklist** |

## Execution plan

1. **Ambiente** (WSL/Debian): `uv venv && uv pip install -e ".[dev]"` ou apt `python3.12-venv` + venv — ver README.
2. **Suíte automatizada (gate principal):**
   ```bash
   pytest
   # ou: uv run pytest
   ```
3. **Ordem sugerida ao implementar gaps:** concluída (T7–T13).
4. **Fixtures:** reutilizar `tests/fixtures/project_yaml/`; adicionar `empty.yaml`, `list_root.yaml` para T11/T12.
5. **Manual smoke (antes de merge/release interno):**
   ```bash
   engineering-agent analyze
   engineering-agent analyze --write-draft   # em tmp clone only — não no repo se architecture.md completo existir
   engineering-agent --version
   ```
6. **Regressão report:** se alterar `build_report`, rodar testes que fixam substrings de seção (T8, T9).

## Out of scope for testing

- Comando `init` e auto-detection (Phase 1).
- Invocação LLM / APIs externas.
- Agente Architect/Reviewer Markdown (workflows Phase 0 manuais).
- Publicação PyPI, CI matrix multi-OS (até existir pipeline).
- Performance, i18n, permissões de filesystem além de tmp_path.
- Reviewer (qualidade de código/segurança) — agente separado.

## Open questions

1. ~~Implementar T7–T9 nesta iteración~~ — feito.
2. Teste M1 vira checklist no PR template ou job CI futuro?
3. Congelar contrato stdout com golden file ou apenas asserts parciais (menos frágil)?
4. `architecture.md` completo no repo impede testar `--write-draft created` no dogfooding — ok usar só tmp_path?

```yaml
# eas-artifact v0.1 — tester
agent: tester
version: "0.1.0"
status: implemented_partial
requirement_ref: .ai/workspace/requirement.md
architecture_ref: .ai/workspace/architecture.md
testing_command: pytest
proposed_cases:
  - id: T7
    type: integration
    priority: must
    description: CLI exit 1 when project.yaml is invalid YAML
    traces_to: "NF3; F3"
  - id: T8
    type: integration
    priority: must
    description: stdout Workspace lists requirement and architecture paths
    traces_to: "AC acceptance #3; F5"
  - id: T9
    type: integration
    priority: must
    description: stdout Recommendation references prompts.md and architect.md
    traces_to: F6
  - id: T10
    type: integration
    priority: should
    description: --version prints package version and exits 0
    traces_to: F1
  - id: T11
    type: unit
    priority: should
    description: empty project.yaml yields stack placeholder in report
    traces_to: "architecture open Q5; schema risk"
  - id: T12
    type: unit
    priority: should
    description: non-mapping YAML root raises ProjectConfigError
    traces_to: loader robustness
  - id: M1
    type: manual
    priority: must
    description: README install path and analyze on EAS repo root
    traces_to: "AC #1; #4"
  - id: M2
    type: manual
    priority: must
    description: verify no LLM invocation from analyze
    traces_to: requirement constraint
summary:
  must: 8
  should: 2
  could: 2
  gaps_high: 0
```
