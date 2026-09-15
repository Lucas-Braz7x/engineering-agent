# Agent: {{AGENT_TITLE}}

```yaml
id: {{AGENT_ID}}
version: 0.1.0
phase: 0
role: {{AGENT_ID}}
review_peer: {{REVIEW_PEER}}   # ou vazio se não houver par
artifact_path: .ai/workspace/{{ARTIFACT_FILE}}
# allowed_tools:              # opcional — só RESTRINGE roles.py
#   - read_file
#   - search_code
#   - write_artifact
```

## Papel

{{RESPONSIBILITY_ONE_PARAGRAPH}}

## Entradas

| Prioridade | Fonte |
|------------|--------|
| Obrigatório | {{REQUIRED_INPUT}} |
| Se existir | `.ai/project.yaml` |
| Se existir | `.ai/rules/*.md` |
| Se existir | Skills em `.ai/skills/**/*.md` relevantes |

## Ferramentas (contrato EAS)

**Permitidas (enforcement com `engineering-agent tools --agent {{AGENT_ID}}`):**

- `{{TOOL_1}}` — {{TOOL_1_WHY}}
- `{{TOOL_2}}` — {{TOOL_2_WHY}}

**Negadas (exemplos):**

- `{{DENIED_TOOL}}` — {{WHY_DENIED}}

Registrar política em `src/eas/runtime/roles.py` (`AGENT_ROLE_POLICIES`).

## Restrições (boundaries)

- **Não** {{BOUNDARY_1}}
- **Não** {{BOUNDARY_2}}

## Modos de falha

| Modo | Sintoma | Resposta | Escalação |
|------|---------|----------|-----------|
| {{FAILURE_1}} | {{SYMPTOM_1}} | {{RESPONSE_1}} | {{ESCALATION_1}} |

## Processo

1. {{STEP_1}}
2. {{STEP_2}}
3. Emitir artefato e preencher YAML `eas-artifact`.

## Artefato de saída

Salvar em **`{{ARTIFACT_PATH}}`**.

### Corpo (Markdown)

Seções H2, nesta ordem:

1. **{{SECTION_1}}**
2. **{{SECTION_2}}**
3. **Open questions**

### Metadados (YAML no final)

```yaml
# eas-artifact v0.1 — {{AGENT_ID}}
agent: {{AGENT_ID}}
version: "0.1.0"
status: draft
{{EXTRA_YAML_KEYS}}
```

## Avaliação

| Critério | Como verificar |
|----------|----------------|
| Schema YAML | `engineering-agent agent validate {{AGENT_ID}} <artifact> --strict` |
| Role policy | `engineering-agent agent show {{AGENT_ID}}` |
| {{CRITERION_3}} | {{HOW_3}} |

## Casos de teste

- [ ] `load_agent(repo, "{{AGENT_ID}}")` sem erro
- [ ] Tool negada retorna erro com `--agent {{AGENT_ID}}`
- [ ] Invoke/prepare gera `invoke.md` com seção "Role boundaries"
- [ ] {{TEST_CASE_4}}

## Invocação

Prompt canônico: `.ai/hosts/prompts.md#{{AGENT_ID}}` (adicionar seção se novo agente).

| Host | Como disparar |
|------|----------------|
| Cursor | `@.ai/agents/{{AGENT_ID}}.md` + requisito |
| CLI | `engineering-agent analyze --agent {{AGENT_ID}} --prepare` |
