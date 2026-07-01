"""
planner/complexity.py

Domain enumeration representing the Planner's estimated execution
complexity for a query.
"""

from enum import Enum, unique


@unique
class Complexity(Enum):
    """
    Represents the Planner's estimated execution complexity for a query.

    Purpose:
        Communicates how much execution effort a query is expected to
        require, so that downstream components (Context Budgeting,
        Model Routing, Observability) can scale their behavior
        accordingly, without the Planner performing that scaling itself.

    Owned by:
        planner/complexity.py

    Consumed by:
        PlannerBuilder, ExecutionPlan. Future: Model Routing, Tool
        Routing, Observability.

    Invariants:
        - A Complexity instance is always exactly one of the members
          defined below; no other values are valid.
        - Complexity carries no routing logic, no model-selection logic,
          and no execution behavior — it is a pure semantic estimate.
        - Membership changes only through an explicit architecture review.
    """

    LOW = "low"
    # Minimal resource / inference effort expected.

    MEDIUM = "medium"
    # Moderate resource / inference effort expected.

    HIGH = "high"
    # Significant resource / inference effort expected.