# Testar o EAS (Phase 0)

Checklist manual — sem CLI ainda. Tempo: **~15 min** (smoke) ou **~45 min** (workflow completo).

## O que você está validando

- O modelo **segue** `.ai/agents/*.md` (seções + YAML `eas-artifact`)
- Artefatos aparecem em `.ai/workspace/`
- Aprovação humana **bloqueia** implementação no workflow feature
- Tester produz `test-plan.md` com casos rastreáveis aos critérios de aceite
- Reviewer produz `findings` e `status` coerentes com o diff

---

## Teste 1 — Smoke: só Architect (~5 min)

**Objetivo:** um `architecture.md` útil sem implementar nada.

### Cursor

1. Abra o repositório no Cursor (rule `eas.mdc` já está ativa).
2. Confira [workspace/requirement.md](workspace/requirement.md) (exemplo já preenchido para este repo).
3. **Agent / Composer**, nova conversa. Envie:

```text
@.ai/agents/architect.md @.ai/workspace/requirement.md

You are running the EAS agent "architect". Follow every instruction in .ai/agents/architect.md.
Read .ai/rules/ and .ai/project.yaml if they exist; explore the repo.
Write the full artifact to .ai/workspace/architecture.md including the eas-artifact YAML block.
```

4. Abra `.ai/workspace/architecture.md` e confira:

- [ ] Todas as 11 seções H2 do architect existem
- [ ] Bloco YAML final com `agent: architect` e `status:`
- [ ] **Open questions** listadas (não inventou requisitos)
- [ ] Plano de implementação **sem** patches de código

### Claude Code

Na raiz do repo:

```text
Read CLAUDE.md, .ai/agents/architect.md, and .ai/workspace/requirement.md.
Run the architect prompt from .ai/hosts/prompts.md.
Write .ai/workspace/architecture.md.
```

---

## Teste 2 — Workflow feature (ponta a ponta)

Siga [workflows/feature.md](workflows/feature.md) ou cole o prompt **feature** de [hosts/prompts.md](hosts/prompts.md).

| Passo | Você faz | Sucesso |
|-------|----------|---------|
| 1 | `requirement.md` preenchido | Critérios de aceite claros |
| 2 | Architect | `architecture.md` + YAML |
| 3 | **Parar** — ler e digitar *"aprovo a arquitetura"* | Agente **não** codifica antes disso |
| 4 | Implementar algo pequeno (ex.: `README.md` + stub `src/`) | Commit no branch |
| 5 | Tester com diff | `test-plan.md` + YAML |
| 6 | Reviewer com diff + test-plan | `code-review.md` + `status` |

**Prompt tester (Cursor):**

```text
@.ai/agents/tester.md @.ai/workspace/requirement.md @.ai/workspace/architecture.md

Run per .ai/agents/tester.md on git diff main...HEAD (or since last commit).
Write .ai/workspace/test-plan.md with eas-artifact YAML.
```

**Prompt reviewer (Cursor):**

```text
@.ai/agents/reviewer.md @.ai/workspace/architecture.md @.ai/workspace/test-plan.md

Run git diff main...HEAD (or diff since last commit) and review per .ai/agents/reviewer.md.
Write .ai/workspace/code-review.md with eas-artifact YAML.
```

Se `main` não existir ou branch único: `git diff HEAD~1` ou liste arquivos manualmente.

---

## Teste 4 — Smoke: Tester (~5 min)

Após uma implementação (ou use o diff do CLI `analyze` já no repo):

```text
@.ai/agents/tester.md @.ai/workspace/architecture.md

Follow .ai/agents/tester.md for the current git diff. Read .ai/rules/testing.md and .ai/project.yaml.
Write .ai/workspace/test-plan.md with eas-artifact YAML.
```

- [ ] Seções H2 na ordem do agente tester
- [ ] Tabela de casos com `must`/`should` e `traces_to`
- [ ] `testing.command` no execution plan (ex.: `pytest`)

---

## Teste 3 — Reviewer sem arquitetura

Útil para validar o agente isolado:

1. Faça uma mudança trivial em qualquer arquivo.
2. Rode só o **reviewer** (sem `@architecture.md`).
3. Esperado: `architecture_alignment: na` no YAML.

---

## Teste em outro repositório

Copie só a pasta `.ai/` + `CLAUDE.md` + `.cursor/rules/eas.mdc` para um projeto real.

1. Ajuste `requirement.md` para uma feature pequena do produto.
2. Repita Teste 1 — a arquitetura deve citar **pastas e stack reais** daquele repo.

---

## Critérios de “passou”

| Artefato | Falha comum | Bom sinal |
|----------|-------------|-----------|
| `architecture.md` | Código completo colado | Componentes + APIs + riscos + plano |
| `architecture.md` | Sem YAML final | `eas-artifact v0.1` presente |
| `test-plan.md` | Lista genérica sem IDs | Casos `T1…` ligados a acceptance criteria |
| `code-review.md` | Vago (“melhorar testes”) | `file` + `line` + `recommendation` |
| Workflow | Implementa antes de aprovar | Pede aprovação explícita no passo 3 |

---

## Limpar entre tentativas

```bash
# opcional — backup antes
mkdir -p .ai/workspace/runs/manual-$(date +%Y%m%d-%H%M)
cp .ai/workspace/*.md .ai/workspace/runs/manual-$(date +%Y%m%d-%H%M)/ 2>/dev/null || true
```

Ou apague só `architecture.md` / `code-review.md` e rode de novo.

---

## Próximo depois de passar

- Conferir [PHASE-0.md](PHASE-0.md) e seguir para **Phase 1**: `engineering-agent init`.
