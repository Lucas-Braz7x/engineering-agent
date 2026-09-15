# Tools

[← Índice](../doc.md)

Os agentes precisam de ferramentas.

**Primeiras:**

- `read_file`, `write_file`, `search_code`
- `run_command`, `run_tests`
- `git_diff`, `git_status`, `git_log`

**Posteriormente:** GitHub, Docker, AWS, database, filesystem, CI

**Abstração possível:**

```python
class Tool:
    name: str

    def execute(self, input):
        ...
```

O agente não precisa saber como a ferramenta funciona internamente.
