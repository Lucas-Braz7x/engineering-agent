# Phase 5 — Autonomous loop

Critério do [roadmap](../docs/roadmap.md): `test → failure → debug → fix plan → retry` com limites.

## Comando

```bash
engineering-agent loop
engineering-agent loop --invoke-agents --force
engineering-agent loop --invoke-agents --suggest-fix --force
engineering-agent loop --invoke-agents --review-on-success --force
engineering-agent loop --max-iterations 3
```

| Flag | Efeito |
|------|--------|
| `--invoke-agents` | Em falha de teste, invoca **debugger** (LLM) |
| `--suggest-fix` | Após debugger, invoca **fixer** → `fix-plan.md` |
| `--review-on-success` | Se testes passam, invoca **reviewer** |
| `--force` | Sobrescreve artefatos existentes |
| `--max-*` | Sobrescreve `limits` do `project.yaml` |

Sem `--invoke-agents`, o loop só roda testes e para em `TESTS_FAILED` ou `SUCCESS`.

## Limites (`project.yaml`)

```yaml
limits:
  max_iterations: 5
  max_command_execution: 20
  max_agent_calls: 30
```

Ao exceder: status `WORKFLOW_BLOCKED` em `.ai/workspace/loop-report.md`.

## Fluxo

```text
┌─────────────┐
│  run_tests  │
└──────┬──────┘
       │ pass ──► SUCCESS (+ reviewer opcional)
       │ fail
       ▼
┌─────────────┐     ┌──────────────┐
│  debugger   │ ──► │ fixer (opt.) │
└──────┬──────┘     └──────────────┘
       │ (human aplica fix-plan / código)
       └──────► próxima iteração até limite
```

O CLI **não aplica patches** automaticamente — `fix-plan.md` orienta a correção manual ou via IDE.

## Exit code

| Code | Meaning |
|------|---------|
| 7 | Loop terminou sem SUCCESS (`TESTS_FAILED` ou `WORKFLOW_BLOCKED`) |

## Requisitos

- `.ai/project.yaml` com `testing.command`
- `--invoke-agents` requer `pip install -e ".[llm]"` e `ANTHROPIC_API_KEY`
