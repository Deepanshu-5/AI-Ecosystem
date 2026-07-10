"""
routing/tool_capability.py

Semantic information-access capabilities selected by Tool Routing.
"""

from enum import Enum, unique


@unique
class ToolCapability(Enum):
    """
    Represents semantic information-access capabilities required by a plan.

    Purpose:
        Communicates required information access without naming concrete
        tools, runtime functions, providers, MCP exposure, or infrastructure.

    Owned by:
        routing/tool_capability.py

    Consumed by:
        ToolRoute and future Tool Execution Integration.

    Invariants:
        - A capability is exactly one of KNOWLEDGE_ACCESS,
          MEMORY_ACCESS, or SESSION_ACCESS.
        - Values are stable semantic identifiers.
        - Contains no routing behavior or infrastructure mapping.
    """

    KNOWLEDGE_ACCESS = "knowledge_access"
    MEMORY_ACCESS = "memory_access"
    SESSION_ACCESS = "session_access"
