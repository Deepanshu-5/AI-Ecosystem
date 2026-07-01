"""
planner/planner_validator.py

Stateless validation of a candidate ExecutionPlan, applied by
PlannerBuilder before an ExecutionPlan is returned to callers.
"""

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import CURRENT_SCHEMA_VERSION, ExecutionPlan
from planner.exceptions import PlannerValidationError
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

_KNOWN_SCHEMA_VERSIONS = frozenset({CURRENT_SCHEMA_VERSION})

_DECISION_TRACE_FIELDS = (
    "processing_goal_reason",
    "complexity_reason",
    "resource_requirements_reason",
)

_RESOURCE_REQUIREMENT_FIELDS = ("knowledge", "memory", "session")


class PlannerValidator:
    """
    Validates a candidate ExecutionPlan before it is returned by
    PlannerBuilder.

    Purpose:
        Performs structural, logical, and semantic validation of a
        candidate ExecutionPlan and reports every violation found in a
        single, precise error. It never repairs, infers, or mutates the
        plan it inspects.

    Owned by:
        planner/planner_validator.py

    Consumed by:
        PlannerBuilder.

    Invariants:
        - Performs no retrieval, no infrastructure access, no
          configuration or environment access.
        - Never mutates the ExecutionPlan or any of its fields.
        - Validation is deterministic and side-effect-free: the same
          ExecutionPlan always produces the same validation result.
        - Validation is exhaustive: all violations across all categories
          are reported together, not just the first one encountered.
    """

    @staticmethod
    def validate(execution_plan: ExecutionPlan) -> None:
        """
        Validate a candidate ExecutionPlan.

        Parameters:
            execution_plan (ExecutionPlan): The candidate plan to
                validate. Not mutated.

        Returns:
            None. Absence of an exception means the plan is valid.

        Raises:
            PlannerValidationError: If one or more structural, logical,
                or semantic violations are found. The message lists
                every violation found, not just the first.

        Side Effects:
            None.
        """
        violations: list[str] = []
        violations.extend(_validate_structural(execution_plan))
        violations.extend(_validate_logical(execution_plan))
        violations.extend(_validate_semantic(execution_plan))

        if violations:
            raise PlannerValidationError(
                "ExecutionPlan failed validation:\n- " + "\n- ".join(violations)
            )


def _validate_structural(plan: ExecutionPlan) -> list[str]:
    """Check that every field has the type the architecture declares."""
    violations: list[str] = []

    if not isinstance(plan, ExecutionPlan):
        return [f"root: expected ExecutionPlan, got {type(plan).__name__}"]

    if not isinstance(plan.processing_goal, ProcessingGoal):
        violations.append(
            f"processing_goal: expected ProcessingGoal, got "
            f"{type(plan.processing_goal).__name__}"
        )

    if not isinstance(plan.complexity, Complexity):
        violations.append(
            f"complexity: expected Complexity, got {type(plan.complexity).__name__}"
        )

    if not isinstance(plan.resource_requirements, ResourceRequirements):
        violations.append(
            f"resource_requirements: expected ResourceRequirements, got "
            f"{type(plan.resource_requirements).__name__}"
        )
    else:
        for field_name in _RESOURCE_REQUIREMENT_FIELDS:
            value = getattr(plan.resource_requirements, field_name)
            if not isinstance(value, bool):
                violations.append(
                    f"resource_requirements.{field_name}: expected bool, got "
                    f"{type(value).__name__}"
                )

    if not isinstance(plan.decision_trace, DecisionTrace):
        violations.append(
            f"decision_trace: expected DecisionTrace, got "
            f"{type(plan.decision_trace).__name__}"
        )
    else:
        for field_name in _DECISION_TRACE_FIELDS:
            value = getattr(plan.decision_trace, field_name)
            if not isinstance(value, str):
                violations.append(
                    f"decision_trace.{field_name}: expected str, got "
                    f"{type(value).__name__}"
                )

    if not isinstance(plan.version, int):
        violations.append(f"version: expected int, got {type(plan.version).__name__}")

    return violations


def _validate_logical(plan: ExecutionPlan) -> list[str]:
    """Check that each field's value is internally consistent."""
    if not isinstance(plan, ExecutionPlan):
        return []

    violations: list[str] = []

    if isinstance(plan.version, int) and plan.version < 1:
        violations.append(f"version: must be >= 1, got {plan.version}")

    if isinstance(plan.decision_trace, DecisionTrace):
        for field_name in _DECISION_TRACE_FIELDS:
            value = getattr(plan.decision_trace, field_name)
            if isinstance(value, str) and not value.strip():
                violations.append(
                    f"decision_trace.{field_name}: must not be empty or "
                    f"whitespace-only"
                )

    return violations


def _validate_semantic(plan: ExecutionPlan) -> list[str]:
    """Check that field values carry valid, recognized meaning."""
    if not isinstance(plan, ExecutionPlan):
        return []

    violations: list[str] = []

    if isinstance(plan.version, int) and plan.version not in _KNOWN_SCHEMA_VERSIONS:
        violations.append(
            f"version: {plan.version} has no known semantic meaning to this "
            f"validator (known versions: {sorted(_KNOWN_SCHEMA_VERSIONS)})"
        )

    return violations