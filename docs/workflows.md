# Workflows

[← Índice](../doc.md)

Workflows coordenam os agentes.

## Feature

```mermaid
flowchart TD
  R[Requirement] --> A[Architect]
  A --> C[Challenger]
  C --> H[Human Approval]
  H --> Co[Coder]
  Co --> T[Tester]
  T --> S[Security]
  S --> Rev[Reviewer]
  Rev --> OK[Approved]
```

## Bug

```text
Bug → Debugger → Root Cause → Coder → Tester → Reviewer
```

## Refactor

```text
Target → Architect → Coder → Tester → Reviewer
```
