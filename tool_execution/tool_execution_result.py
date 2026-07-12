"""Immutable public contract for completed ToolRoute execution."""

from __future__ import annotations

from dataclasses import dataclass

from tool_execution.tool_result import ToolResult

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ToolExecutionResult:
    """Ordered immutable results produced from a ToolRoute."""

    results: tuple[ToolResult, ...]
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Return a stable, versioned serialization preserving result order."""
        return {
            "results": [result.to_dict() for result in self.results],
            "version": self.version,
        }
