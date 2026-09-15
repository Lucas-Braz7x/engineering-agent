# Exemplo de uso final

[← Índice](../doc.md)

Projeto Go (`torrent-uploader`):

```bash
cd torrent-uploader
engineering-agent init
```

```text
Detected:
  Language: Go
  Framework: Gin
  Database: PostgreSQL
  Testing: Go testing
  Container: Docker
  Git: yes
```

```bash
engineering-agent feature "Add resumable file uploads"
```

**Pipeline:**

```text
ARCHITECT      → architecture.md
CHALLENGER     → challenge.md
Human approval
CODER          → implementation
TESTER         → test-plan.md
SECURITY       → security-review.md
REVIEWER       → code-review.md
```

**Resumo final (exemplo):**

```text
✓ Feature implemented

Files changed: 8
Tests added: 14
Security findings: 0
Review status: APPROVED

Artifacts:
  .ai/workspace/architecture.md
  .ai/workspace/challenge.md
  .ai/workspace/test-plan.md
  .ai/workspace/security-review.md
  .ai/workspace/code-review.md
```
