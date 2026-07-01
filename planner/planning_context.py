"""
planner/planning_context.py

Internal immutable domain object representing the Planner's intermediate
analysis before an ExecutionPlan is constructed.

PlanningContext exists only within the Planner package and is never
exposed outside it.
"""

from __future__ import annotations

from dataclasses import dataclass

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


@dataclass(frozen=True)
class PlanningContext:
    """
    Internal immutable container for intermediate Planner decisions.

    Purpose:
        Carries the Planner's analyzed decision state from QueryAnalyzer
        to PlannerBuilder before the final ExecutionPlan is created.

        PlanningContext is an implementation detail of the Planner.
        Downstream components must never depend on it.

    Owned by:
        planner/planning_context.py

    Consumed by:
        QueryAnalyzer
        PlannerBuilder

    Invariants:
        - Immutable once constructed.
        - Exists only within the Planner package.
        - Contains only domain objects.
        - Contains no runtime state.
        - Contains no infrastructure references.
        - Contains no execution logic.
        - Deterministic for identical input.
    """

    processing_goal: ProcessingGoal
    complexity: Complexity
    resource_requirements: ResourceRequirements
    decision_trace: DecisionTrace

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]:
                Stable representation of this PlanningContext.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "processing_goal": self.processing_goal.value,
            "complexity": self.complexity.value,
            "resource_requirements": self.resource_requirements.to_dict(),
            "decision_trace": self.decision_trace.to_dict(),
        }