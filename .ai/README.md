# EAS — Phase 0 (Markdown)

Agentes e workflows executados **manualmente** no **Cursor**, **Claude Code** ou outro host com acesso ao repo.

Documentação do produto: [doc.md](../doc.md).

## Começar

1. **Testar:** [TESTING.md](TESTING.md) (smoke architect em ~5 min)
2. Escolha o host: [hosts/README.md](hosts/README.md) (Cursor · Claude Code)
3. Edite [workspace/requirement.md](workspace/requirement.md) se quiser outro exercício
4. Siga [workflows/feature.md](workflows/feature.md)
5. Use os prompts em [hosts/prompts.md](hosts/prompts.md)

## Entrada por ferramenta

| Ferramenta | Arquivo na raiz do repo |
|------------|-------------------------|
| Cursor | `.cursor/rules/eas.mdc` |
| Claude Code | `CLAUDE.md` |

## Agentes

| Agente | Definição | Artefato |
|--------|-----------|----------|
| Architect | [agents/architect.md](agents/architect.md) | `workspace/architecture.md` |
| Reviewer | [agents/reviewer.md](agents/reviewer.md) | `workspace/code-review.md` |

Definições de agente são **agnósticas de IDE**; hosts só mudam como anexar contexto.
