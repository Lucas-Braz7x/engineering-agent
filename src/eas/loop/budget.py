from __future__ import annotations

from dataclasses import dataclass

from eas.context.limits import LoopLimits


class LoopBlockedError(Exception):
    """Autonomy limits exceeded — WORKFLOW_BLOCKED."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass
class LoopBudget:
    limits: LoopLimits
    iterations: int = 0
    command_executions: int = 0
    agent_calls: int = 0

    def check_can_continue(self) -> None:
        if self.iterations >= self.limits.max_iterations:
            raise LoopBlockedError(
                "Maximum iterations reached. Human intervention required."
            )
        if self.command_executions >= self.limits.max_command_execution:
            raise LoopBlockedError(
                "Maximum command executions reached. Human intervention required."
            )
        if self.agent_calls >= self.limits.max_agent_calls:
            raise LoopBlockedError(
                "Maximum agent calls reached. Human intervention required."
            )

    def begin_iteration(self) -> None:
        self.check_can_continue()
        self.iterations += 1

    def record_command(self) -> None:
        self.command_executions += 1
        if self.command_executions > self.limits.max_command_execution:
            raise LoopBlockedError(
                "Maximum command executions reached. Human intervention required."
            )

    def record_agent(self) -> None:
        self.agent_calls += 1
        if self.agent_calls > self.limits.max_agent_calls:
            raise LoopBlockedError(
                "Maximum agent calls reached. Human intervention required."
            )
