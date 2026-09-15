# Requirement

Exercício de smoke test do EAS neste repositório (Phase 0).

## Title

CLI `engineering-agent analyze` (especificação + stub mínimo)

## Problem

Hoje só existem docs e `.ai/` em Markdown. Precisamos do primeiro comando executável que prove o core: carregar contexto do projeto e produzir um artefato de análise, alinhado ao [primeiro MVP](../../docs/primeiro-mvp.md).

## User story

Como desenvolvedor, quero rodar `engineering-agent analyze` na raiz de um repo para obter um resumo estruturado da stack e recomendações iniciais, sem depender do Cursor para orquestrar agentes.

## Acceptance criteria

- [ ] Pacote Python em `src/eas/` com entrypoint CLI documentado no README
- [ ] Comando `analyze` lê `.ai/project.yaml` se existir; caso contrário, mensagem clara (init ainda não implementado)
- [ ] Saída inclui caminho sugerido para `.ai/workspace/architecture.md` ou gera um rascunho mínimo
- [ ] `pyproject.toml` com dependências mínimas (ex.: typer ou click)
- [ ] Teste unitário trivial do módulo de contexto (load yaml)

## Constraints

- Manter Phase 0: agentes continuam em Markdown; CLI não substitui architect, só prepara terreno para Phase 2
- Sem integração LLM na primeira entrega — pode ser placeholder que imprime “invoke architect via .ai/hosts/prompts.md”
- Python 3.11+

## Out of scope

- `init` com auto-detection completa (Phase 1)
- Invocação automática de API Anthropic/OpenAI
- Publicação em PyPI
