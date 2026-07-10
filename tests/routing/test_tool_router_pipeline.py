import pytest

from planner.planner_builder import PlannerBuilder
from planner.query_analyzer import QueryAnalyzer
from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from routing.tool_router import ToolRouter
from routing.tool_routing_validator import ToolRoutingValidator


PIPELINE_CASES = [
    (
        "Hello there",
        (),
    ),
    (
        "What is Python?",
        (ToolCapability.KNOWLEDGE_ACCESS,),
    ),
    (
        "Recall my preference",
        (ToolCapability.MEMORY_ACCESS,),
    ),
    (
        "Continue from earlier",
        (ToolCapability.SESSION_ACCESS,),
    ),
    (
       "What do you know and remember from earlier?",
      (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    ),
  ),
]


def _build_plan(query: str):
    context = QueryAnalyzer.analyze(query)
    return PlannerBuilder.build(
        processing_goal=context.processing_goal,
        complexity=context.complexity,
        resource_requirements=context.resource_requirements,
        decision_trace=context.decision_trace,
    )


@pytest.mark.parametrize(("query", "expected_capabilities"), PIPELINE_CASES)
def test_planner_to_tool_router_pipeline(query, expected_capabilities):
    plan = _build_plan(query)
    before = plan.to_dict()

    route = ToolRouter.route(plan)

    assert plan.to_dict() == before
    assert isinstance(route, ToolRoute)
    assert route.capabilities == expected_capabilities
    ToolRoutingValidator.validate_output(route)
    ToolRoutingValidator.validate_routing_invariant(plan, route)


@pytest.mark.parametrize(("query", "expected_capabilities"), PIPELINE_CASES)
def test_planner_to_tool_router_pipeline_is_deterministic(
    query,
    expected_capabilities,
):
    first_plan = _build_plan(query)
    second_plan = _build_plan(query)

    first_route = ToolRouter.route(first_plan)
    second_route = ToolRouter.route(second_plan)

    assert first_plan.to_dict() == second_plan.to_dict()
    assert first_route == second_route
    assert first_route.to_dict() == second_route.to_dict()
    assert first_route.capabilities == expected_capabilities
