class ToolError(Exception):
    """Tool execution failed."""


class ToolPolicyError(ToolError):
    """Path or command blocked by safety policy."""
