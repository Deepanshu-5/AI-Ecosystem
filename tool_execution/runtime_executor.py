"""Provider-independent runtime execution boundary contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from routing.tool_capability import ToolCapability
from tool_execution.tool_result import ToolResult


class RuntimeExecutor(ABC):
    """Execute one semantic capability without exposing infrastructure."""

    @abstractmethod
    def execute(self, capability: ToolCapability) -> ToolResult:
        """Execute ``capability`` and return its semantic ToolResult."""
