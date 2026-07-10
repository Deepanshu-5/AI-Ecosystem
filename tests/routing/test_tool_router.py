import pytest

import routing.tool_router as tool_router_module
from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements
from routing.exceptions import ToolRoutingValidationError
from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from routing.tool_router import ToolRouter


ROUTING_CASES = [
    (
        False,
        False,
        False,
        (),
        "no resource access capabilities required",
    ),
    (
        False,
        False,
        True,
        (ToolCapability.SESSION_ACCESS,),
        "session requirement routes to session access capability",
    ),
    (
        False,
        True,
        False,
        (ToolCapability.MEMORY_ACCESS,),
        "memory requirement routes to memory access capability",
    ),
    (
        False,
        True,
        True,
        (ToolCapability.MEMORY_ACCESS, ToolCapability.SESSION_ACCESS),
        "memory and session requirements route to memory and session access capabilities",
    ),
    (
        True,
        False,
        False,
        (ToolCapability.KNOWLEDGE_ACCESS,),
        "knowledge requirement routes to knowledge access capability",
    ),
    (
        True,
        False,
        True,
        (ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.SESSION_ACCESS),
        "knowledge and session requirements route to knowledge and session access capabilities",
    ),
    (
        True,
        True,
        False,
        (ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.MEMORY_ACCESS),
        "knowledge and memory requirements route to knowledge and memory access capabilities",
    ),
    (
        True,
        True,
        True,
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
]


def _plan(
    knowledge: bool = False,
    memory: bool = False,
    session: bool = False,
    complexity: Complexity = Complexity.LOW,
    processing_goal: ProcessingGoal = ProcessingGoal.GENERAL,
    decision_trace: DecisionTrace | None = None,
) -> ExecutionPlan:
    return ExecutionPlan(
        processing_goal=processing_goal,
        complexity=complexity,
        resource_requirements=ResourceRequirements(
            knowledge=knowledge,
            memory=memory,
            session=session,
        ),
        decision_trace=decision_trace
        or DecisionTrace(
            processing_goal_reason="General query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="No retrieval is required.",
        ),
    )


@pytest.mark.parametrize(
    ("knowledge", "memory", "session", "expected_capabilities", "expected_reason"),
    ROUTING_CASES,
)
def test_tool_router_exhaustive_matrix(
    knowledge,
    memory,
    session,
    expected_capabilities,
    expected_reason,
):
    plan = _plan(knowledge=knowledge, memory=memory, session=session)
    before = plan.to_dict()

    route = ToolRouter.route(plan)

    assert isinstance(route, ToolRoute)
    assert route.capabilities == expected_capabilities
    assert route.reason == expected_reason
    assert plan.to_dict() == before


@pytest.mark.parametrize(
    ("knowledge", "memory", "session", "expected_capabilities", "expected_reason"),
    ROUTING_CASES,
)
def test_tool_router_is_deterministic(
    knowledge,
    memory,
    session,
    expected_capabilities,
    expected_reason,
):
    plan = _plan(knowledge=knowledge, memory=memory, session=session)

    first_route = ToolRouter.route(plan)
    second_route = ToolRouter.route(plan)

    assert first_route == second_route
    assert first_route.capabilities == expected_capabilities
    assert second_route.reason == expected_reason


@pytest.mark.parametrize("complexity", tuple(Complexity))
def test_tool_router_is_complexity_independent(complexity):
    plan = _plan(knowledge=True, complexity=complexity)

    route = ToolRouter.route(plan)

    assert route.capabilities == (ToolCapability.KNOWLEDGE_ACCESS,)


@pytest.mark.parametrize("processing_goal", tuple(ProcessingGoal))
def test_tool_router_is_processing_goal_independent(processing_goal):
    plan = _plan(memory=True, processing_goal=processing_goal)

    route = ToolRouter.route(plan)

    assert route.capabilities == (ToolCapability.MEMORY_ACCESS,)


def test_tool_router_is_decision_trace_independent():
    first_plan = _plan(
        session=True,
        decision_trace=DecisionTrace(
            processing_goal_reason="First trace.",
            complexity_reason="First trace.",
            resource_requirements_reason="First trace.",
        ),
    )
    second_plan = _plan(
        session=True,
        decision_trace=DecisionTrace(
            processing_goal_reason="Second trace.",
            complexity_reason="Second trace.",
            resource_requirements_reason="Second trace.",
        ),
    )

    assert ToolRouter.route(first_plan) == ToolRouter.route(second_plan)


def test_tool_router_rejects_unsupported_input():
    with pytest.raises(ToolRoutingValidationError):
        ToolRouter.route("not a plan")


def test_tool_router_has_no_default_route(monkeypatch):
    plan = _plan()
    monkeypatch.delitem(
        tool_router_module._ROUTE_BY_REQUIREMENTS,
        (False, False, False),
    )

    with pytest.raises(ToolRoutingValidationError):
        ToolRouter.route(plan)


def test_tool_router_has_no_fallback_route_for_invalid_state():
    plan = _plan()
    object.__setattr__(plan.resource_requirements, "knowledge", "yes")

    with pytest.raises(ToolRoutingValidationError):
        ToolRouter.route(plan)
