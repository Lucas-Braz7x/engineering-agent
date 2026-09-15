# Phase 0 — checklist de conclusão

Critério do [roadmap](../docs/roadmap.md): agentes em Markdown + workflow Feature + processo validado manualmente.

## Agentes

| Agente | Definição | Artefato | Status |
|--------|-----------|----------|--------|
| Architect | [agents/architect.md](agents/architect.md) | `workspace/architecture.md` | ✅ |
| Tester | [agents/tester.md](agents/tester.md) | `workspace/test-plan.md` | ✅ |
| Reviewer | [agents/reviewer.md](agents/reviewer.md) | `workspace/code-review.md` | ✅ |

## Workflow & hosts

| Item | Path | Status |
|------|------|--------|
| Feature workflow | [workflows/feature.md](workflows/feature.md) | ✅ |
| Prompts canônicos | [hosts/prompts.md](hosts/prompts.md) | ✅ |
| Cursor bootstrap | `.cursor/rules/eas.mdc` | ✅ |
| Claude bootstrap | `CLAUDE.md` | ✅ |

## Rules (mínimo)

| Rule | Path |
|------|------|
| Architecture | [rules/architecture.md](rules/architecture.md) |
| Coding | [rules/coding.md](rules/coding.md) |
| Testing | [rules/testing.md](rules/testing.md) |

## Validação manual

| Exercício | Guia |
|-----------|------|
| Smoke architect | [TESTING.md](TESTING.md#teste-1--smoke-só-architect-5-min) |
| Workflow completo | [TESTING.md](TESTING.md#teste-2--workflow-feature-ponta-a-ponta) |
| Smoke tester | [TESTING.md](TESTING.md#teste-4--smoke-tester) |

## Fora da Phase 0 (próximas fases)

- `engineering-agent init` (detecção) — **Phase 1**
- Challenger, Coder, Security como agentes dedicados
- CLI orquestrando agentes / LLM — **Phase 2+**
- `engineering-agent feature` automatizado — **Phase 4**

**Nota:** O stub `engineering-agent analyze` já existe (adiantou Phase 2); não substitui os agentes Markdown.
