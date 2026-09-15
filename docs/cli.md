# CLI

[← Índice](../doc.md)

```bash
engineering-agent init
engineering-agent init --dry-run
engineering-agent analyze
engineering-agent analyze --agent architect --prepare
engineering-agent analyze --agent architect --invoke
engineering-agent context status
engineering-agent memory add "Uses Zod for validation"
engineering-agent context search zod
engineering-agent agent show architect
engineering-agent agent validate architect .ai/workspace/architecture.md
engineering-agent tools --agent architect list
engineering-agent tools list
engineering-agent tools read-file README.md
engineering-agent tools git-diff --base main --head HEAD
engineering-agent tools run-tests
engineering-agent feature --prepare --step architect
engineering-agent feature --invoke --all --assume-approved --force
engineering-agent review --invoke --force --git-base main --git-head HEAD
engineering-agent bug "stack trace" --invoke --step debugger --force
engineering-agent status
engineering-agent loop
engineering-agent loop --invoke-agents --suggest-fix --force
engineering-agent integrations status
engineering-agent integrations github --pr 1
engineering-agent integrations ci --limit 5
engineering-agent --version
```

Phase 6 integrations: [`.ai/PHASE-6.md`](../.ai/PHASE-6.md). Requer `gh` / `docker` / `aws` no PATH conforme o subcomando.

Phase 4 workflows: [`.ai/PHASE-4.md`](../.ai/PHASE-4.md). `--invoke` requer `pip install -e ".[llm]"` e `ANTHROPIC_API_KEY`.

Comandos futuros (roadmap): `debug`, `test` (automação além dos agentes).
