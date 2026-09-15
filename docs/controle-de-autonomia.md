# Controle de autonomia

[← Índice](../doc.md)

Impedir loops infinitos (ex.: Coder → Test → Failure → Coder → …).

```yaml
limits:
  max_iterations: 5
  max_command_execution: 20
  max_agent_calls: 30
```

Se exceder: `WORKFLOW_BLOCKED` — *Maximum iterations reached. Human intervention required.*
