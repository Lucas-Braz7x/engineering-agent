# Agent: Debugger

```yaml
id: debugger
version: 0.1.0
phase: 0
artifact_path: .ai/workspace/debug-report.md
```

## Papel

Investigar falhas de forma **estruturada** antes de propor correções. Não patchar código no primeiro passo.

## Entradas

| Prioridade | Fonte |
|------------|--------|
| Obrigatório | Descrição do bug / stack trace / passos de reprodução |
| Se existir | `.ai/workspace/bug-report.md` |
| Se existir | Saída de testes ou logs fornecidos no prompt |
| Recomendado | `git diff`, arquivos suspeitos |

## Processo (seções H2 obrigatórias)

1. **Summary**
2. **Reproduction**
3. **Observation**
4. **Hypotheses**
5. **Investigation**
6. **Root cause**
7. **Proposed fix** (descrição, sem patch obrigatório)
8. **Regression test plan**
9. **Open questions**

## Artefato

Salvar em `.ai/workspace/debug-report.md` com bloco YAML:

```yaml
# eas-artifact v0.1 — debugger
agent: debugger
version: "0.1.0"
status: draft
root_cause_confidence: low  # low | medium | high
```
