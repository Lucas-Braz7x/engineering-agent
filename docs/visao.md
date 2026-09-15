# Visão

[← Índice](../doc.md)

O **Engineering Agent System (EAS)** é uma ferramenta de engenharia de software orientada a agentes.

A ideia é permitir que um desenvolvedor execute tarefas como:

```bash
engineering-agent init
engineering-agent analyze
engineering-agent feature "Implement large file upload"
engineering-agent review
engineering-agent debug
engineering-agent test
```

O sistema analisa o projeto atual, identifica sua stack e utiliza diferentes agentes especializados para trabalhar sobre o código.

**O sistema não deve ser limitado a uma linguagem específica.**

Exemplos de stack suportada conceitualmente:

- Python + FastAPI
- TypeScript + NestJS
- Go + Gin
- Java + Spring
- Rust
- C#
- …

O **core** do EAS permanece independente da linguagem.
