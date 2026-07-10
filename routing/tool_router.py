"""
routing/tool_router.py

Deterministic Tool Router implementation for Tool Routing V1.
"""

from planner.execution_plan import ExecutionPlan

from routing.exceptions import ToolRoutingValidationError
from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from routing.tool_routing_validator import ToolRoutingValidator

_ROUTE_BY_REQUIREMENTS = {
    (False, False, False): (
        (),
        "no resource access capabilities required",
    ),
    (False, False, True): (
        (ToolCapability.SESSION_ACCESS,),
        "session requirement routes to session access capability",
    ),
    (False, True, False): (
        (ToolCapability.MEMORY_ACCESS,),
        "memory requirement routes to memory access capability",
    ),
    (False, True, True): (
        (ToolCapability.MEMORY_ACCESS, ToolCapability.SESSION_ACCESS),
        "memory and session requirements route to memory and session access capabilities",
    ),
    (True, False, False): (
        (ToolCapability.KNOWLEDGE_ACCESS,),
        "knowledge requirement routes to knowledge access capability",
    ),
    (True, False, True): (
        (ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.SESSION_ACCESS),
        "knowledge and session requirements route to knowledge and session access capabilities",
    ),
    (True, True, False): (
        (ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.MEMORY_ACCESS),
        "knowledge and memory requirements route to knowledge and memory access capabilities",
    ),
    (True, True, True): (
        (
            ToolCapability.KNOWLEDGE_ACCESS,
            ToolCapability.MEMORY_ACCESS,
            ToolCapability.SESSION_ACCESS,
        ),
        (
            "knowledge, memory, and session requirements route to knowledge, "
            "memory, and session access capabilities"
        ),
    ),
}


class ToolRouter:
    """
    Routes an ExecutionPlan to semantic information-access capabilities.

    Purpose:
        Implements the frozen V1 resource-requirements-only routing
        policy and returns the canonical immutable ToolRoute output.

    Owned by:
        routing/tool_router.py

    Consumed by:
        Future Tool Execution Integration and routing tests.

    Invariants:
        - ExecutionPlan is the only input contract.
        - ExecutionPlan.resource_requirements is the only
          capability-selection authority.
        - ProcessingGoal is boundary-validated but does not affect
          capability selection in V1.
        - Performs no query analysis, trace parsing, tool discovery,
          runtime resolution, configuration lookup, fallback, retry, or
          tool execution.
        - Never mutates Planner domain objects.
    """

    @staticmethod
    def route(execution_plan: ExecutionPlan) -> ToolRoute:
        """
        Route an ExecutionPlan to a ToolRoute.

        Parameters:
            execution_plan (ExecutionPlan): Planner output to route.

        Returns:
            ToolRoute: Immutable semantic tool routing output.

        Raises:
            ToolRoutingValidationError: If input, output, or the routing
            invariant is invalid.

        Side Effects:
            None.
        """
        ToolRoutingValidator.validate_input(execution_plan)

        requirements = execution_plan.resource_requirements
        requirement_state = (
            requirements.knowledge,
            requirements.memory,
            requirements.session,
        )

        capabilities_and_reason = _ROUTE_BY_REQUIREMENTS.get(requirement_state)
        if capabilities_and_reason is None:
            raise ToolRoutingValidationError(
                "Tool Routing policy failed validation:\n- "
                f"requirements state {requirement_state!r} has no "
                "configured V1 route"
            )

        capabilities, reason = capabilities_and_reason
        tool_route = ToolRoute(capabilities=capabilities, reason=reason)

        ToolRoutingValidator.validate_output(tool_route)
        ToolRoutingValidator.validate_routing_invariant(
            execution_plan=execution_plan,
            tool_route=tool_route,
        )

        return tool_route
