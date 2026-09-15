# Testing Rules

1. Prefer pytest for Python in this repository (`testing.command` in project.yaml).
2. Unit tests must not require network or external services unless marked integration.
3. CLI tests should use `typer.testing.CliRunner` or subprocess against an installed package.
4. Fixtures live under `tests/fixtures/`; keep them minimal and readable.
5. Every bug fix should include a regression test when feasible.
