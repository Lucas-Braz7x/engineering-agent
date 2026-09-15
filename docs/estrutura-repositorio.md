# Estrutura inicial do repositório

[← Índice](../doc.md)

Começar **pequeno**:

```text
engineering-agent-system/
├── .ai/
│   ├── agents/
│   │   ├── architect.md
│   │   ├── reviewer.md
│   │   └── tester.md
│   ├── hosts/           # Cursor, Claude Code — prompts e guias
│   │   ├── prompts.md
│   │   ├── cursor.md
│   │   └── claude-code.md
Curti │   ├── skills/
│   │   └── general/
│   ├── rules/
│   │   ├── architecture.md
│   │   └── coding.md
│   └── workflows/
│       └── feature.md
├── .cursor/rules/
│   └── eas.mdc          # bootstrap Cursor
├── CLAUDE.md            # bootstrap Claude Code
├── src/
│   └── eas/
│       ├── agents/
│       ├── workflows/
│       ├── tools/
│       ├── context/
│       └── adapters/
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

Não criar inicialmente todos os agentes.
