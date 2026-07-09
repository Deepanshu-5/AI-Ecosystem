"""
routing/model_router.py

Deterministic Model Router implementation for Model Routing V1.
"""

from planner.complexity import Complexity
from planner.execution_plan import ExecutionPlan

from routing.exceptions import ModelRoutingValidationError
from routing.model_route import ModelRoute
from routing.model_routing_validator import ModelRoutingValidator
from routing.model_target import ModelTarget

_ROUTE_BY_COMPLEXITY = {
    Complexity.LOW: (
        ModelTarget.LIGHTWEIGHT,
        "low complexity routes to lightweight target",
    ),
    Complexity.MEDIUM: (
        ModelTarget.STANDARD,
        "medium complexity routes to standard target",
    ),
    Complexity.HIGH: (
        ModelTarget.ADVANCED,
        "high complexity routes to advanced target",
    ),
}


class ModelRouter:
    """
    Routes an ExecutionPlan to a semantic ModelTarget.

    Purpose:
        Implements the frozen V1 complexity-only routing policy and
        returns the canonical immutable ModelRoute output.

    Owned by:
        routing/model_router.py

    Consumed by:
        Future Model Execution Integration and routing tests.

    Invariants:
        - ExecutionPlan is the only input contract.
        - ExecutionPlan.complexity is the only target-selection authority.
        - ProcessingGoal is boundary-validated but does not affect target
          selection in V1.
        - Performs no prompt inspection, provider resolution,
          configuration lookup, fallback, retry, or model execution.
        - Never mutates Planner domain objects.
    """

    @staticmethod
    def route(execution_plan: ExecutionPlan) -> ModelRoute:
        """
        Route an ExecutionPlan to a ModelRoute.

        Parameters:
            execution_plan (ExecutionPlan): Planner output to route.

        Returns:
            ModelRoute: Immutable semantic model routing output.

        Raises:
            ModelRoutingValidationError: If input, output, or the routing
            invariant is invalid.

        Side Effects:
            None.
        """
        ModelRoutingValidator.validate_input(execution_plan)

        target_and_reason = _ROUTE_BY_COMPLEXITY.get(execution_plan.complexity)
        if target_and_reason is None:
            raise ModelRoutingValidationError(
                "Model Routing policy failed validation:\n- "
                f"complexity {execution_plan.complexity.value!r} has no "
                "configured V1 route"
            )

        target, reason = target_and_reason
        model_route = ModelRoute(target=target, reason=reason)

        ModelRoutingValidator.validate_output(model_route)
        ModelRoutingValidator.validate_routing_invariant(
            execution_plan=execution_plan,
            model_route=model_route,
        )

        return model_route
