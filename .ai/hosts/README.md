# Hosts (Cursor, Claude Code, …)

O EAS é **agnóstico de IDE**: agentes, rules e workflows vivem em `.ai/`; cada **host** só define como carregar contexto e disparar o mesmo prompt.

```text
.ai/agents/*.md  ──┐
.ai/workflows/    ├──► Host (Cursor | Claude Code | …) ──► Modelo + tools
.ai/rules/        ──┘
```

## Contrato (igual em todos os hosts)

1. Ler a definição do agente em `.ai/agents/<id>.md`
2. Carregar entradas listadas na tabela **Entradas** do agente
3. Escrever o artefato no path `artifact_path` do agente (YAML no topo)
4. Respeitar schemas `eas-artifact` / `eas-approval` nos outputs

Prompts canônicos (copiar/colar): **[prompts.md](prompts.md)**

## Hosts suportados na Phase 0

| Host | Guia | Entrada no repositório |
|------|------|-------------------------|
| **Cursor** | [cursor.md](cursor.md) | [.cursor/rules/eas.mdc](../../.cursor/rules/eas.mdc) |
| **Claude Code** | [claude-code.md](claude-code.md) | [CLAUDE.md](../../CLAUDE.md) na raiz |

## Configuração opcional

Em `.ai/project.yaml` (quando existir):

```yaml
host:
  default: cursor  # cursor | claude_code | generic
```

Isso é documentação para humanos/CLI futura; nenhum host é obrigatório.

## Host genérico

Qualquer chat com acesso a arquivos do repo:

1. Abra `.ai/agents/<agent>.md` e `.ai/hosts/prompts.md`
2. Cole o prompt da seção correspondente
3. Peça para gravar o artefato no path indicado
