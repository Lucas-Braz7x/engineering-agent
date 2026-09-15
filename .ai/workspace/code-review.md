# Code review — CLI `engineering-agent analyze` (Phase 0)

## Review summary

A implementação entrega o stub acordado em `.ai/workspace/architecture.md`: pacote `src/eas/`, subcomando `analyze` com Typer, loader tolerante de `project.yaml`, relatório stdout em blocos fixos, `--write-draft` idempotente e exit codes 0/1/2. A separação `cli` → `commands.analyze` → `context` / `analysis` espelha o desenho e mantém Phase 0 sem LLM. **Sete testes pytest passaram** (`uv run pytest -q`). Não há findings **high**; alguns gaps menores de teste e um desvio documental leve em `find_repo_root`. **Recomendação: merge / seguir para uso.**

## Scope reviewed

| Item | Valor |
|------|--------|
| Base | `bea1761` (initial) |
| Head | `ebc39b4` (`main`, working tree clean) |
| Commits relevantes | `70a5567` feat(cli), `6224c53` docs README, `ed50088` project.yaml, `ebc39b4` uv.lock |
| Arquivos (código + testes) | 20 arquivos no feat + `pyproject.toml`, `README.md`, `.ai/project.yaml`, `uv.lock` |
| Comandos | `uv run pytest -q` → **7 passed** |
| Arquitetura de referência | `.ai/workspace/architecture.md` |

## Architecture alignment

**Parcial → praticamente sim** para o MVP:

| Decisão (architecture) | Implementação |
|------------------------|---------------|
| Typer + PyYAML | `pyproject.toml`, `loader.py` com `safe_load` |
| `analyze [--path] [--write-draft]` | `commands/analyze.py` |
| Exit 0 / 1 / 2 | `EXIT_*` + `typer.Exit` |
| Draft só se ausente | `draft.py` → `skipped (exists)` |
| Sem LLM; pointer prompts | `report.py` → Recommendation block |
| `project.yaml` dogfooding | `.ai/project.yaml` em commit dedicado |
| `find_repo_root` sobe até `.ai/` | `paths.py` — **não** usa `.git` como fallback (ver F2) |
| Pastas reservadas vazias | `adapters/`, `agents/`, `tools/`, `workflows/` |

O **Current state** dentro de `architecture.md` ainda descreve “sem código Python”; isso é drift do artefato architect, não do código (F4).

## Findings

| ID | Sev. | Category | File | Issue | Recommendation |
|----|------|----------|------|-------|----------------|
| F1 | low | testing | `tests/test_analyze.py` | YAML inválido coberto só no loader; CLI não testa exit **1** em `analyze`. | Adicionar teste com `project.yaml` malformado e `assert result.exit_code == 1`. |
| F2 | low | architecture | `src/eas/context/paths.py` | Arquitetura citava heurística `.ai/` **ou** `.git`; só `.ai/` é considerado. | Aceitável (yaml vive em `.ai/`); opcional: subir até `.git` se `.ai/project.yaml` existir no root walk. |
| F3 | low | maintainability | `src/eas/cli.py` | `Optional[bool]` enquanto o resto usa `str \| None` / 3.11 style. | Unificar para `bool \| None` no callback de `--version`. |
| F4 | low | maintainability | `.ai/workspace/architecture.md` | Seção *Current state* desatualizada pós-implementação. | Atualizar artefato ou adicionar nota “implemented in 70a5567” (fora do diff de código). |
| F5 | low | testing | `tests/test_analyze.py` | Sem assert das **linhas fixas** do contrato stdout (ex. ordem `Stack:` / `Workspace:`). | Opcional: snapshot parcial das seções para evitar regressão no formato. |

Nenhum finding de **security** relevante: leitura local, `yaml.safe_load`, sem execução de `testing.command`/`build.command`.

## Test & verification gaps

- [x] Loader: válido / ausente / YAML inválido (`test_context_loader.py`)
- [x] CLI: missing yaml (exit 2), success, `--write-draft`, subdirectory `--path`
- [ ] CLI: parse error → exit 1
- [ ] Smoke manual documentado no README não re-executado nesta review (ambiente sem `engineering-agent` no PATH global; `uv run` OK)

## Suggested next steps

1. (Opcional antes do merge) Teste CLI para YAML inválido — F1.
2. Gravar `.ai/workspace/approval.md` no workflow se ainda não existir para o passo de implementação.
3. Atualizar `architecture.md` *Current state* ou arquivar em `.ai/workspace/runs/` — F4.
4. Phase 1: `engineering-agent init` e alinhar `find_repo_root` com auto-detection.

```yaml
# eas-artifact v0.1 — reviewer
agent: reviewer
version: "0.1.0"
status: APPROVED
reviewed_at: "2026-03-15T22:15:00-03:00"
scope:
  base_ref: bea1761
  head_ref: ebc39b4
  files_count: 24
architecture_alignment: yes
findings:
  - id: F1
    severity: low
    category: testing
    file: tests/test_analyze.py
    line: null
    issue: No CLI test for invalid project.yaml (exit code 1)
    recommendation: Add typer CliRunner test with malformed YAML under .ai/
  - id: F2
    severity: low
    category: architecture
    file: src/eas/context/paths.py
    line: 15
    issue: find_repo_root only checks .ai/, not .git fallback from architecture text
    recommendation: Document as intentional or extend heuristic in Phase 1
  - id: F3
    severity: low
    category: maintainability
    file: src/eas/cli.py
    line: 25
    issue: Optional[bool] inconsistent with codebase typing style
    recommendation: Use bool | None
  - id: F4
    severity: low
    category: maintainability
    file: .ai/workspace/architecture.md
    line: 34
    issue: Current state still says no Python code in repo
    recommendation: Update architect artifact after implementation
  - id: F5
    severity: low
    category: testing
    file: tests/test_analyze.py
    line: null
    issue: stdout contract not fully asserted
    recommendation: Add section-order assertions in success test
summary:
  high: 0
  medium: 0
  low: 5
```
