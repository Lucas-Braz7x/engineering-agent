# Auto-detection

[← Índice](../doc.md)

O comando `engineering-agent init` deve analisar o projeto.

**Possíveis sinais:**

- `package.json`, `pyproject.toml`, `requirements.txt`
- `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`
- `Dockerfile`, `docker-compose.yml`

**Exemplo de saída:**

```text
$ engineering-agent init

Detecting project...

✓ TypeScript
✓ Node.js
✓ NestJS
✓ pnpm
✓ PostgreSQL
✓ Jest
✓ Docker
✓ Git

Project context generated: .ai/project.yaml
```

O usuário poderá revisar e alterar o resultado.

## Phase 1.1

- **Rust:** `Cargo.toml` (`cargo test` / `cargo build`, frameworks axum, actix, rocket)
- **Java:** `pom.xml` (Maven) ou `build.gradle` / `build.gradle.kts` (Gradle)
- **Monorepo:** vários manifestos na raiz → todos os sinais no terminal; `project.yaml` usa stack primária + bloco `detection:`

Prioridade da stack primária: `pyproject.toml` → `package.json` → `go.mod` → `Cargo.toml` → `pom.xml` → Gradle.
