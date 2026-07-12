"""Immutable public contract for one semantic tool execution outcome."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from routing.tool_capability import ToolCapability

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ToolResult:
    """The immutable, versioned result of one executed ToolCapability."""

    capability: ToolCapability
    payload: Mapping[str, object]
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Return the stable public representation of this execution fact."""
        return {
            "capability": self.capability.value,
            "payload": self.payload,
            "version": self.version,
        }
