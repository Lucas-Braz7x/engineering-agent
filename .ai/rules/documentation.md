# Documentation Rules

Regras para o agente **Documenter** e para humanos que editam docs no repo.

## Onde escrever

| Tipo | Path |
|------|------|
| Documentação do produto | `docs/**/*.md`, `doc.md`, `README.md` |
| Architecture Decision Records | `docs/adr/NNNN-short-slug.md` |
| Relatório da execução do agente | `.ai/workspace/documentation-report.md` (artefato EAS) |
| Design de feature em andamento | `.ai/workspace/architecture.md` (Architect — não duplicar aqui) |

Slug ADR: minúsculas, hífens, sem acentos (ex.: `0003-use-sqlite-for-context-store.md`).

## Quando criar ADR

Crie ADR quando a decisão:

- afeta estrutura de módulos, boundaries ou contratos públicos;
- introduz dependência ou tecnologia nova com trade-offs;
- é difícil de reverter ou precisa ser lembrada em meses;
- foi debatida com alternativas em `architecture.md`.

Não crie ADR para typos, renomeações cosméticas ou detalhes de uma PR isolada sem impacto durável.

## Template ADR

Copie e preencha em `docs/adr/NNNN-title.md`:

```markdown
# NNNN. Title

- Status: Proposed | Accepted | Superseded by NNNM
- Date: YYYY-MM-DD

## Context

What is the issue or force that motivates this decision?

## Decision

What is the change we are proposing or have agreed to?

## Consequences

What becomes easier or harder? What are follow-ups?

## Alternatives considered

Brief list of options not chosen and why.
```

Atualize [docs/adr/README.md](../../docs/adr/README.md) com uma linha na tabela de índice quando adicionar ADR.

## Tom e estilo

- Português ou inglês: siga a língua dominante do arquivo que você edita.
- Frases curtas; exemplos de comando quando útil.
- Links relativos entre docs (`[texto](../outro.md)`).
