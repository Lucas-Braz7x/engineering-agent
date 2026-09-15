# Phase 2 — Python CLI runtime

Critério do [roadmap](../docs/roadmap.md): `analyze` carrega contexto, rules, skills, prepara ou invoca agente e grava artefato.

## Entregas

| Item | Status |
|------|--------|
| Carregar `.ai/project.yaml`, rules, skills, requirement | ✅ `eas/runtime/load_context.py` |
| Carregar manifest do agente (`.ai/agents/*.md`) | ✅ repo ou **bundled** no pacote |
| Montar prompt de invocação | ✅ `eas/runtime/build_prompt.py` |
| `--prepare` → `.ai/workspace/runs/<id>/invoke.md` | ✅ |
| `--invoke` → Anthropic + artefato (opcional `[llm]`) | ✅ |
| Relatório `analyze` com bloco Context | ✅ |

## Comandos

```bash
engineering-agent analyze
engineering-agent analyze --agent architect --prepare
engineering-agent analyze --agent architect --invoke   # ANTHROPIC_API_KEY
pip install -e ".[llm]"
```

## Variáveis de ambiente

| Variável | Uso |
|----------|-----|
| `ANTHROPIC_API_KEY` | Obrigatória para `--invoke` |
| `EAS_ANTHROPIC_MODEL` | Modelo (default `claude-sonnet-4-20250514`) |

## Fora da Phase 2

- Workflows `feature` / `review` automatizados (Phase 4)
- Tools filesystem/git/shell (Phase 3)
- Agentes Coder, Challenger, Security dedicados
