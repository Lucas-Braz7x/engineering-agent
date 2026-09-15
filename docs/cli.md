# CLI

[← Índice](../doc.md)

Primeira interface:

```bash
engineering-agent init          # Phase 1: auto-detect → .ai/project.yaml
engineering-agent init --dry-run
engineering-agent analyze
engineering-agent analyze --agent architect --prepare   # Phase 2: invoke bundle
engineering-agent analyze --agent architect --invoke    # Phase 2: LLM + artifact
engineering-agent feature "Implement file upload"
engineering-agent review
engineering-agent debug
engineering-agent test
engineering-agent status
```
