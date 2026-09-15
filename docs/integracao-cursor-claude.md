# Integração com Cursor / Claude

[← Índice](../doc.md)

Inicialmente o EAS **não** substitui Cursor nem Claude Code — **orquestra** o mesmo conhecimento em `.ai/` para qualquer host.

```text
Engineering Agent System
          ↓
     .ai/  (agents, workflows, rules, workspace)
          ↓
   Host adapter (Cursor | Claude Code | …)
          ↓
      Repository
```

## Princípio

| Camada | Onde | Conteúdo |
|--------|------|----------|
| **Core EAS** | `.ai/agents/`, `.ai/workflows/`, `.ai/rules/` | Contratos e processos — **um só lugar** |
| **Prompts** | `.ai/hosts/prompts.md` | Texto canônico copiado em qualquer IDE |
| **Host** | `.ai/hosts/cursor.md`, `.ai/hosts/claude-code.md` | Como carregar contexto e gravar artefatos |
| **Bootstrap** | `.cursor/rules/eas.mdc`, `CLAUDE.md` | Ponteiros curtos para o modelo ao abrir o repo |

Agentes, schemas `eas-artifact` e paths de workspace **não** duplicam por IDE.

## Cursor

- Rule always-on: [`.cursor/rules/eas.mdc`](../.cursor/rules/eas.mdc)
- Mencionar arquivos com `@.ai/...` no chat
- Detalhes: [`.ai/hosts/cursor.md`](../.ai/hosts/cursor.md)

## Claude Code

- Instruções de projeto: [`CLAUDE.md`](../CLAUDE.md) na raiz
- Pedir leitura explícita de paths (`.ai/agents/...`) — sem `@`
- Detalhes: [`.ai/hosts/claude-code.md`](../.ai/hosts/claude-code.md)

## Claude.ai (web)

Sem filesystem: colar definição do agente + requirement + prompt de [`.ai/hosts/prompts.md`](../.ai/hosts/prompts.md) e copiar o artefato para `.ai/workspace/` manualmente.

## Configuração futura

`.ai/project.yaml` pode declarar `host.default` para a CLI; na Phase 0 é opcional.

## Evolução

O runtime próprio (Python) usará os mesmos manifests; só trocará o host manual por invocação programática — ver [evolucao-runtime.md](evolucao-runtime.md).
