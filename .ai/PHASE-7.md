# Phase 7 — Role boundaries (code-enforced)

Inspiração: comportamento de agente não deve depender só do prompt. Cada agente é um **componente com permissões**.

## Modelo

```
Agent manifest (.ai/agents/*.md)
  + role policy (eas.runtime.roles)
  + allowed_tools (subset enforced in CLI)
  + required artifact YAML keys
  + optional review_peer (pares tipo Architect ↔ Reviewer)
  + validation on --invoke
```

## CLI

```bash
engineering-agent agent list
engineering-agent agent show architect
engineering-agent agent validate architect .ai/workspace/architecture.md --strict
engineering-agent agent coder-profile

engineering-agent tools --agent architect list
engineering-agent tools --agent architect read-file README.md
engineering-agent tools --agent architect write-artifact --content "# ..."
```

Sem `--agent`, as tools continuam disponíveis (modo humano/IDE). Com `--agent`, `execute()` bloqueia tools fora da política.

## Tools por papel (resumo)

| Agent | Pode | Não pode (exemplos) |
|-------|------|---------------------|
| architect | read, search, write_artifact, git log/status | write_file, run_command, git_diff |
| reviewer | read, search, diff, tests, write_artifact, gh/ci read | write_file, run_command |
| tester | read, search, diff, tests, write_artifact | write_file |
| debugger | + run_command | write_file |
| fixer | read, diff, tests, write_artifact | write_file |
| coder (perfil) | write_file, tests, diff | write_artifact |

`write_artifact` só grava no `artifact_path` do agente ou em `.ai/workspace/runs/**/*.md`.

## Overrides

No manifest YAML, `allowed_tools` pode **restringir** (nunca expandir) a lista definida em código.

## Pares review_peer

Declarados no manifest e repetidos em `invoke.md` para o host alinhar revisão com desenho/implementação.
