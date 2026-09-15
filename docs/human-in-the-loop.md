# Human-in-the-loop

[← Índice](../doc.md)

O sistema **não** deve ser totalmente autônomo por padrão.

```text
Architect → Challenger → ┌ Architecture ready ─┐
                         │ Approve? [y/N]      │
                         └─────────────────────┘
```

**Configuração exemplo:**

```yaml
approval:
  architecture: required
  security: required
  code_changes: automatic
```
