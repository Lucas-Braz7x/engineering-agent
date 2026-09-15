# Engineering Agent System (EAS)

This repository uses **`.ai/`** for agents, workflows, rules, and workspace artifacts. IDE-specific steps live under **`.ai/hosts/`**.

## Quick start

1. Edit `.ai/workspace/requirement.md`
2. Follow `.ai/workflows/feature.md`
3. Use prompts from `.ai/hosts/prompts.md` (same text as Cursor)

## When I ask for EAS / architect / tester / reviewer / feature workflow

- Read the agent definition in `.ai/agents/<name>.md` and obey it completely
- Read inputs listed in that file (requirement, `project.yaml`, `rules/`, repo as needed)
- Write outputs to the path in the agent manifest (`artifact_path`), including the `eas-artifact` YAML footer
- Do not skip human approval gates described in `.ai/workflows/feature.md`

Details: `.ai/README.md` · Claude Code host: `.ai/hosts/claude-code.md`
