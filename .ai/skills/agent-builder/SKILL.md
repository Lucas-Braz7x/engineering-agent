---
name: agent-builder
description: >-
  Cria agentes EAS completos (não só prompts): responsabilidade, tools com
  limites em código, artefatos, falhas, avaliação e testes. Use quando o
  usuário pedir para criar/definir um agente, skill de agente, ou "Create an
  agent for this task".
---

# Agent Builder (EAS)

Agentes **não são apenas prompts**. São **sistemas de software** com:

- definição de papel e contrato (Markdown + manifest YAML)
- **ferramentas permitidas e negadas** (enforcement no CLI quando `--agent` está definido)
- artefatos e schema `eas-artifact`
- estado e memória (`.eas/eas.db`, Phase 8)
- loops e workflows (`.ai/workflows/`)
- **avaliação** e critérios de sucesso/falha
- **testes** que provam o comportamento, não só o texto do prompt

Referências no repo:

| Peça | Onde |
|------|------|
| Agente exemplo | `.ai/agents/architect.md` |
| Políticas de tools | `src/eas/runtime/roles.py` |
| Validação de artefato | `src/eas/runtime/validate_artifact.py` |
| Catálogo de tools | `src/eas/tools/registry.py` |
| Role boundaries | `.ai/PHASE-7.md` |
| Context store | `.ai/PHASE-8.md` |

Templates desta skill: `templates/agent.md`, `templates/tool.py`, `templates/evaluator.py`.

---

## Quando disparar

- "Crie um agente para…"
- "Create an agent for this task"
- Novo papel no workflow (ex.: explain, security-auditor, agent-builder)
- Refatorar agente que hoje é só um prompt solto

---

## Prompt canônico (usar com o host)

```text
Create an agent for this task.

Requirements:
- define its responsibility
- define available tools
- define boundaries
- define failure modes
- define evaluation criteria
- define test cases
```

Traduza o pedido do usuário em artefatos concretos no repo (ver checklist abaixo). **Não** pare no prompt do IDE.

---

## Checklist de entrega (ordem)

### 1. Responsabilidade

- Um parágrafo: **o que faz** e **o que explicitamente não faz**
- Entradas obrigatórias (tabela Prioridade | Fonte)
- Processo em passos numerados
- Artefato de saída: path em `.ai/workspace/` + seções H2 obrigatórias

### 2. Ferramentas disponíveis

- Liste tools do catálogo EAS (`engineering-agent tools list`) ou novas tools registradas
- No manifest YAML, opcional: `allowed_tools` (só pode **restringir** a política em `roles.py`)
- Par **review_peer** quando houver par revisão (ex.: architect ↔ reviewer)

### 3. Limites (boundaries)

- **Prompt:** restrições em "## Restrições"
- **Código:** entrada em `AGENT_ROLE_POLICIES` em `src/eas/runtime/roles.py` com `allowed_tools` mínimos
- Registrar agente em `_ALLOWED_AGENTS` em `src/eas/runtime/load_agent.py`
- Cópia bundled: `src/eas/bundled/agents/<id>.md` espelhando `.ai/agents/<id>.md`
- Documentar aliases negados (`edit_source` → `write_file`, etc.) em PHASE-7

### 4. Modos de falha (failure modes)

Tabela no agente:

| Modo | Sintoma | Resposta do agente | Escalação |
|------|---------|-------------------|-----------|
| Entrada insuficiente | Falta requisito/diff | Listar em Open questions; não inventar | Humano |
| Tool negada | CLI exit 5 com "not allowed" | Usar tool permitida ou pedir agente certo | Ajustar role |
| Artefato inválido | `validate_artifact` falha | Corrigir YAML/seções H2 | Re-invoke |
| Loop / orçamento | `WORKFLOW_BLOCKED` | Parar; relatório em `loop-report.md` | Humano |

### 5. Critérios de avaliação

- **Automáticos:** `engineering-agent agent validate <id> <artifact> --strict`
- **Política:** pytest para tools/roles se mudou código
- **Qualitativos:** rubrica no próprio agente (seção "Evaluation" ou checklist no artefato)

Use `templates/evaluator.py` como esboço de avaliador local (sem LLM).

### 6. Casos de teste

- Mínimo: teste de carga do manifest (`load_agent`)
- Teste de policy: agente X não pode `write_file` (ver `tests/test_roles.py`)
- Teste de artefato fake no invoke (YAML obrigatório)
- Se novo workflow: `tests/test_workflows.py` ou comando documentado

---

## Fluxo de criação rápido

1. Copiar `templates/agent.md` → `.ai/agents/<id>.md` e preencher.
2. Adicionar `AgentRolePolicy` em `roles.py` + manifest `role` / `review_peer`.
3. Se precisar tool nova: copiar `templates/tool.py`, registrar em `registry.py`, documentar em `.ai/PHASE-3.md`.
4. `engineering-agent agent show <id>` — conferir allowed/denied.
5. `engineering-agent analyze --agent <id> --prepare` — revisar `invoke.md` (memórias + role boundaries).
6. Implementar avaliador/casos em `tests/` ou script derivado de `templates/evaluator.py`.

---

## Anti-padrões

- Agente "você é um ótimo especialista" sem tools nem validação
- `write_file` para agentes de design/review
- Artefato sem bloco `eas-artifact` YAML
- Expandir `allowed_tools` no YAML além do que `roles.py` permite
- Esquecer par de revisão quando o workflow assume alinhamento (architect → implementação → reviewer)

---

## Invocação no Cursor

```
@.ai/skills/agent-builder/SKILL.md
@.ai/agents/architect.md   (referência de formato)

Create an agent for this task: <descreva a tarefa>
```

Siga o checklist e escreva arquivos no repo; não apenas responda no chat.
