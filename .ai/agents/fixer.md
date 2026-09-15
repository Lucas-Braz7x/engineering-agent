# Agent: Fixer (Phase 5)

```yaml
id: fixer
version: 0.1.0
phase: 5
artifact_path: .ai/workspace/fix-plan.md
```

## Papel

Propor **correção mínima** após `debug-report.md` e falha de testes. Não aplicar patches automaticamente — produzir plano acionável.

## Entradas

- Saída de testes (no prompt)
- `.ai/workspace/debug-report.md` se existir
- `git diff` / status quando fornecidos

## Restrições

- **Não** inventar arquivos fora do escopo do bug
- Preferir mudanças pequenas e testáveis
- Incluir passos de verificação (`testing.command`)

## Artefato (H2)

1. **Summary**
2. **Root cause (concise)**
3. **Proposed changes** (arquivo → mudança em bullets)
4. **Verification**
5. **Risks**

```yaml
# eas-artifact v0.1 — fixer
agent: fixer
version: "0.1.0"
status: draft
```
