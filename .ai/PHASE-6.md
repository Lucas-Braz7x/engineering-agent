# Phase 6 — Integrações (read-only)

Critério do [roadmap](../docs/roadmap.md): GitHub, AWS, Docker e CI/CD via CLIs oficiais, sem mutações automáticas.

## Comandos

```bash
engineering-agent integrations status
engineering-agent integrations github
engineering-agent integrations github --pr 42
engineering-agent integrations docker
engineering-agent integrations aws
engineering-agent integrations ci --limit 10
```

Também disponíveis no catálogo `engineering-agent tools list` (`github_*`, `docker_*`, `aws_*`, `ci_*`).

## Requisitos

| Integração | CLI | Notas |
|------------|-----|--------|
| GitHub | `gh` | `pr view`, `run list`; remote via `git` |
| Docker | `docker` | `compose ps` / `config --services` |
| AWS | `aws` | `sts get-caller-identity` apenas |
| CI | `gh` + workflows | Lista `.github/workflows` e runs recentes |

`integrations status` só inspeciona o filesystem e PATH (não chama APIs).

## Config (`project.yaml`)

```yaml
integrations:
  github:
    remote: origin
  docker:
    compose_file: docker-compose.yml
  aws:
    profile: my-profile   # opcional
  ci:
    provider: github_actions
```

## Segurança

- Subprocessos fixos: apenas `gh`, `docker`, `aws` (ver `eas.integrations.proc`).
- Sem `shell=True`; timeout e truncamento de saída alinhados às tools da Phase 3.

## Exit code

Subcomandos `integrations` (exceto `status`) retornam **8** em falha de integração.
