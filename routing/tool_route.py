"""
routing/tool_route.py

Immutable canonical output contract for Tool Routing.
"""

from dataclasses import dataclass

from routing.tool_capability import ToolCapability

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ToolRoute:
    """
    The immutable routing decision produced by ToolRouter.

    Purpose:
        Captures the selected semantic information-access capabilities
        and the deterministic reason for that selection.

    Owned by:
        routing/tool_route.py

    Consumed by:
        Future Tool Execution Integration and routing tests.

    Invariants:
        - Immutable once constructed.
        - Contains exactly capabilities, reason, and version.
        - capabilities is a tuple of valid ToolCapability members.
        - reason is deterministic, non-empty text.
        - version is a supported ToolRoute schema version.
        - Contains no concrete tool names, arguments, execution order,
          runtime state, execution plan, or infrastructure bindings.
    """

    capabilities: tuple[ToolCapability, ...]
    reason: str
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order:
            capabilities, reason, version. Capabilities are serialized
            using enum values.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "capabilities": [
                capability.value for capability in self.capabilities
            ],
            "reason": self.reason,
            "version": self.version,
        }
