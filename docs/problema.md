# Problema

[← Índice](../doc.md)

Ferramentas como Cursor, Claude Code e outros agentes de programação são extremamente capazes, mas normalmente o desenvolvedor precisa fornecer manualmente:

- contexto do projeto
- padrões arquiteturais
- regras de código
- comandos de teste
- conhecimento da stack
- critérios de revisão
- processo para desenvolvimento de features
- processo para debugging

Além disso, diferentes tarefas exigem diferentes perspectivas.

Uma única instrução como *"Implemente essa feature"* mistura arquitetura, implementação, testes, segurança e revisão.

O EAS propõe **separar essas responsabilidades em agentes especializados**, coordenados por **workflows**.
