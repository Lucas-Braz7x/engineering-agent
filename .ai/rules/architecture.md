# Architecture Rules

Regras do projeto para agentes EAS (Architect, Coder, Reviewer). Ajuste conforme o time.

1. Business logic must not depend on infrastructure details.
2. External services must be isolated behind clear interfaces.
3. Avoid unnecessary abstractions — prefer the simplest design that meets stated requirements.
4. New dependencies require justification in the architecture artifact or PR description.
5. Prefer extending existing patterns in the repo over introducing new frameworks.
