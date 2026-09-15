from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoopLimits:
    max_iterations: int = 5
    max_command_execution: int = 20
    max_agent_calls: int = 30


def parse_limits(data: dict[str, Any]) -> LoopLimits:
    block = data.get("limits")
    if not isinstance(block, dict):
        return LoopLimits()
    return LoopLimits(
        max_iterations=int(block.get("max_iterations", 5)),
        max_command_execution=int(block.get("max_command_execution", 20)),
        max_agent_calls=int(block.get("max_agent_calls", 30)),
    )
