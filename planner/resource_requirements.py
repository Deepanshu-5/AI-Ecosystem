"""
planner/resource_requirements.py

Domain object representing which ecosystem resources a query requires.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceRequirements:
    """
    Represents which ecosystem resources are required to fulfill a query.

    Purpose:
        Declares which upstream layers (Knowledge, Memory, Session) must
        be consulted to fulfill a query, so that downstream components
        retrieve only what is actually needed instead of unconditionally
        querying every layer.

    Owned by:
        planner/resource_requirements.py

    Consumed by:
        PlannerBuilder, ExecutionPlan. Future: Execution Layer,
        Context Budgeting integration.

    Invariants:
        - knowledge, memory, and session are plain booleans; no other
          types are valid.
        - ResourceRequirements never performs retrieval — it only
          declares which retrieval is needed.
        - Instances are immutable once constructed.
    """

    knowledge: bool
    memory: bool
    session: bool

    def to_dict(self) -> dict[str, bool]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, bool]: Mapping of resource name to whether it is
            required. Key order is fixed: knowledge, memory, session.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "knowledge": self.knowledge,
            "memory": self.memory,
            "session": self.session,
        }