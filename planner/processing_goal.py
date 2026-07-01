"""
planner/processing_goal.py

Domain enumeration representing the category of problem a user query
maps to, as determined by the Planner.
"""

from enum import Enum, unique


@unique
class ProcessingGoal(Enum):
    """
    Represents what kind of problem the user has submitted to the
    AI Ecosystem.

    Purpose:
        Communicates the high-level category of a query so that
        downstream components (Context Budgeting, Routing, Execution,
        Observability) can apply goal-specific behavior without the
        Planner needing to know how each goal is ultimately fulfilled.

    Owned by:
        planner/processing_goal.py

    Consumed by:
        PlannerBuilder, ExecutionPlan, Routing Layer (future),
        Observability (future)

    Invariants:
        - A ProcessingGoal instance is always exactly one of the members
          defined below; no other values are valid.
        - ProcessingGoal carries no behavior, retrieval logic, or routing
          logic — it is a pure semantic classification.
        - Membership changes only through an explicit architecture review.
    """

    GENERAL = "general"
    # The query does not require specialized domain handling.

    KNOWLEDGE = "knowledge"
    # The query requires retrieval from the Knowledge Layer (documents, facts).

    MEMORY = "memory"
    # The query requires retrieval from persistent user Memory.

    SESSION = "session"
    # The query depends on current or prior conversation/session context.

    DOCUMENT = "document"
    # The query concerns a specific uploaded or referenced document.

    CODE = "code"
    # The query concerns source code understanding, generation, or review.