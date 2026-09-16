# Phase 4 — Workflows (CLI)

Critério do [roadmap](../docs/roadmap.md): comandos `feature`, `bug`, `review`.

## Comandos

| Comando | Workflow | Agentes |
|---------|----------|---------|
| `engineering-agent feature` | feature | architect → tester → reviewer → documenter |
| `engineering-agent review` | review | reviewer → documenter (+ git diff) |
| `engineering-agent bug` | bug | debugger → tester → reviewer → documenter |
| `engineering-agent status` | — | lista artefatos em `.ai/workspace/` |

Padrão: exatamente um de `--prepare` ou `--invoke`.

```bash
# Feature (após requirement.md)
engineering-agent feature --prepare --step architect
engineering-agent feature --invoke --step architect --force
# … implementação manual …
engineering-agent feature --invoke --all --assume-approved --force

# Review
engineering-agent review --invoke --force --git-base main --git-head HEAD

# Bug
engineering-agent bug "stack trace …" --invoke --step debugger --force
engineering-agent bug --invoke --all --assume-approved --force
```

## Gates

| Workflow | Antes de tester/reviewer |
|----------|---------------------------|
| feature | `.ai/workspace/approval.md` com `decision: approved` **ou** `--assume-approved` |
| bug | `debug-report.md` existe **ou** `--assume-approved` após fix |

## Contexto automático

Para tester, reviewer e debugger o runtime anexa ao prompt:

- `git diff` / `git status`
- artefatos existentes (`architecture.md`, `test-plan.md`, …)
- `--with-tests` inclui saída de `run_tests` no reviewer

## Exit code

| Code | Meaning |
|------|---------|
| 6 | Workflow error (gate, missing requirement, invoke failure) |

## Fora da Phase 4

- Coder / Challenger / Security automatizados
- Loops autônomos (Phase 5)
