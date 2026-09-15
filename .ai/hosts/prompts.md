# Prompts canônicos (todos os hosts)

Substitua `<…>` antes de enviar. Os hosts **não** alteram o texto — só mudam como anexar arquivos.

---

## architect

```text
You are running the EAS agent "architect". Follow every instruction in .ai/agents/architect.md.

Requirement:
<paste .ai/workspace/requirement.md or describe the feature>

Before answering:
- Read .ai/project.yaml and .ai/rules/ if they exist
- Explore the repository as needed for current state

Deliver the full artifact and write it to .ai/workspace/architecture.md (include the eas-artifact YAML block at the end).
```

---

## reviewer

```text
You are running the EAS agent "reviewer". Follow every instruction in .ai/agents/reviewer.md.

Review the current changes (git diff against main, or the files I specify).
Compare with .ai/workspace/architecture.md when it exists.

Deliver the full artifact and write it to .ai/workspace/code-review.md (include the eas-artifact YAML block at the end).
```

---

## feature (workflow Phase 0)

```text
We are executing .ai/workflows/feature.md (Phase 0, manual mode).

1) Confirm you read .ai/workspace/requirement.md (or ask me to fill it).
2) Run the architect agent (.ai/agents/architect.md) and save .ai/workspace/architecture.md.
3) Stop and ask for my explicit approval before any implementation.
4) After I implement and notify you, run the reviewer agent (.ai/agents/reviewer.md) on the current diff and save .ai/workspace/code-review.md.
```
