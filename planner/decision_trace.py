"""
planner/decision_trace.py

Domain object representing the Planner's structured explanation for the
decisions captured in an ExecutionPlan.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionTrace:
    """
    A structured, human-readable explanation describing why the Planner
    reached its decisions.

    Purpose:
        Makes Planner reasoning inspectable without reverse-engineering
        the implementation. DecisionTrace exists only for explainability
        and debugging — it never changes planner decisions, and no
        component may branch its behavior based on its contents.

    Owned by:
        planner/decision_trace.py

    Consumed by:
        Observability, Debugging. Never consumed by decision-making
        components (PlannerBuilder, Routing, Execution).

    Invariants:
        - Each reason is a human-readable string explaining exactly one
          of the three decisions captured alongside it in ExecutionPlan.
        - DecisionTrace has no effect on planning, routing, or execution
          outcomes — removing it must never change system behavior.
        - Instances are immutable once constructed.
    """

    processing_goal_reason: str
    complexity_reason: str
    resource_requirements_reason: str

    def to_dict(self) -> dict[str, str]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, str]: Mapping of decision name to its human-readable
            reason. Key order is fixed: processing_goal_reason,
            complexity_reason, resource_requirements_reason.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "processing_goal_reason": self.processing_goal_reason,
            "complexity_reason": self.complexity_reason,
            "resource_requirements_reason": self.resource_requirements_reason,
        }