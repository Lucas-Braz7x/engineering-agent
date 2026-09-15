# Contexto do projeto

[← Índice](../doc.md)

Cada projeto possui contexto próprio:

```text
.ai/
├── project.yaml
├── agents/
├── skills/
├── rules/
└── workspace/
```

**Exemplo de `project.yaml`:**

```yaml
project:
  name: file-uploader

language:
  name: typescript
  version: "22"

framework:
  name: nestjs

package_manager:
  name: pnpm

database:
  name: postgresql

testing:
  command: pnpm test

build:
  command: pnpm build
```
