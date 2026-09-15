# Host: Claude Code

## Entrada automática

O arquivo [CLAUDE.md](../../CLAUDE.md) na raiz do repositório é lido pelo Claude Code e aponta para `.ai/`.

## Carregar contexto

Claude Code lê arquivos via ferramentas do CLI — não use `@` como no Cursor.

| Objetivo | Ação |
|----------|------|
| Definição do agente | Pedir: *"Read .ai/agents/architect.md and follow it"* ou incluir o path no prompt |
| Requisito | Garantir que `.ai/workspace/requirement.md` existe; referenciar no prompt |
| Rules / project | *"Read .ai/rules/ and .ai/project.yaml if present"* |
| Diff para review | Rodar `git diff main...HEAD` no terminal e pedir review, ou deixar o Claude executar o comando |

## Executar um agente

1. Copie o prompt de [prompts.md](prompts.md) (**architect** ou **reviewer**)
2. Na mesma sessão, confirme leitura de `.ai/agents/<agent>.md`
3. Exija escrita em disco: *"Write the output to .ai/workspace/architecture.md"* (paths relativos à raiz do repo)

Exemplo mínimo no terminal Claude Code:

```text
Read .ai/agents/architect.md and .ai/workspace/requirement.md.
Then run the architect prompt from .ai/hosts/prompts.md.
Write the artifact to .ai/workspace/architecture.md.
```

## Workflow feature

Siga [.ai/workflows/feature.md](../workflows/feature.md). Use o prompt **feature** em [prompts.md](prompts.md) para uma sessão guiada.

## Claude.ai (web) — fora do repo

Se o código não estiver montado no Claude Code:

1. Cole o conteúdo de `.ai/agents/<agent>.md` + `requirement.md` na conversa
2. Cole o prompt de [prompts.md](prompts.md)
3. Copie a resposta manualmente para `.ai/workspace/<artifact>.md`

Artefatos em `.ai/workspace/` continuam sendo a fonte de verdade; o host só muda o transporte.

## Dicas

- Mantenha `CLAUDE.md` curto — detalhes ficam em `.ai/`
- Para parity com Cursor, use os mesmos paths de artefato (`artifact_path` no YAML de cada agente)
- Skills Anthropic no disco (`.claude/skills/`) são opcionais; o EAS usa `.ai/skills/` quando existir
