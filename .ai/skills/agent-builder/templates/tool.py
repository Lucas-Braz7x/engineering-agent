"""
Template: registrar uma tool EAS (Phase 3+).

Passos:
1. Implementar função em eas/tools/<module>.py (ToolContext -> ToolResult)
2. Registrar em eas/tools/registry.py (TOOL_CATALOG + branch em execute)
3. Adicionar subcomando em eas/commands/tools_cmd.py se exposta no CLI
4. Incluir ou negar a tool em AgentRolePolicy (eas/runtime/roles.py)
5. Teste em tests/test_tools.py ou tests/test_roles.py
"""
from __future__ import annotations

from eas.tools.models import ToolContext, ToolResult


def example_tool(ctx: ToolContext, *, argument: str) -> ToolResult:
    """Substitua por comportamento real; mantenha paths sob ctx.root."""
    if not argument.strip():
        return ToolResult(ok=False, output="", error="argument is required")
    return ToolResult(ok=True, output=f"example: {argument}")


# registry.py — adicionar ao TOOL_CATALOG:
#     "example_tool": "One-line description for agents and CLI list",
#
# registry.py — em execute():
#     if name == "example_tool":
#         return example_tool(ctx, argument=kwargs["argument"])
