# Host: Cursor

## Entrada automática

A rule [.cursor/rules/eas.mdc](../../.cursor/rules/eas.mdc) instrui o agente a tratar `.ai/` como fonte de verdade para workflows EAS.

## Carregar contexto

| Método | Uso |
|--------|-----|
| `@.ai/agents/architect.md` | Mencionar arquivos no chat |
| `@.ai/workspace/requirement.md` | Requisito atual |
| `@Folder .ai/rules` | Rules do projeto (quando existir) |
| Composer / Agent | Preferir modo com leitura e escrita no workspace |

## Executar um agente

1. Abra [prompts.md](prompts.md) → seção **architect** ou **reviewer**
2. Mencione `@.ai/agents/<agent>.md` na mesma mensagem (reforça o contrato)
3. Envie; confira se `architecture.md` / `code-review.md` foi gravado em `.ai/workspace/`

## Workflow feature

Siga [.ai/workflows/feature.md](../workflows/feature.md) ou use o prompt **feature** em [prompts.md](prompts.md).

## Dicas

- Para review com diff: peça explicitamente `git diff main...HEAD` ou use terminal integrado antes do prompt reviewer.
- Histórico de runs: `.ai/workspace/runs/<id>/` — peça ao agente para não sobrescrever a última execução se quiser comparar.
