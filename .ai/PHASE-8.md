# Phase 8 — Context System persistente

`.ai/` permanece configuração humana versionável. Estado operacional fica em `.eas/eas.db` (ignorado pelo Git).

## Layout

```
.ai/          # agents, rules, skills, workflows, workspace
.eas/
  eas.db      # SQLite (WAL)
```

## Tabelas

| Tabela | Conteúdo |
|--------|----------|
| `projects` | Repo root + nome |
| `tasks` | Workflow / loop / analyze |
| `runs` | prepare + invoke por `run_id` |
| `messages` | system / user / assistant (truncados) |
| `decisions` | eventos (artifact_written, falhas) |
| `memories` | `candidate` \| `active` \| `rejected` |
| `artifacts` | path relativo + sha256 |

Busca: FTS5 quando disponível; senão `LIKE`.

## Memória curada

- Artefatos podem gerar **candidatas** (heurística em linhas tipo “uses X for validation”).
- Só `memory promote` ou `memory add` torna memória **ativa**.
- Memórias ativas entram no `invoke.md` com orçamento (itens/caracteres).

## CLI

```bash
engineering-agent context status
engineering-agent context search "zod"
engineering-agent context history
engineering-agent context prune          # dry-run
engineering-agent context prune --apply
engineering-agent context vacuum

engineering-agent memory list
engineering-agent memory add "Uses Zod for validation"
engineering-agent memory candidates
engineering-agent memory promote 3
engineering-agent memory reject 3
engineering-agent memory forget 3
```

## Retenção (default)

Config opcional em `.ai/project.yaml`:

```yaml
context:
  retention:
    run_retention_days: 30
    min_recent_runs: 20
    candidate_retention_days: 14
    auto_prune_interval_hours: 24
```

`prune` não apaga arquivos em `.ai/workspace/` — só linhas no SQLite.

## Desabilitar

`EAS_CONTEXT=0` — CLI principal segue; store não é aberto.

## Recuperação

Apague `.eas/eas.db` para recriar; `.ai/` não é alterado por `prune`.
