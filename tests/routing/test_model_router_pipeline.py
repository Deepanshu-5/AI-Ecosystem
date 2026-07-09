import pytest

from planner.complexity import Complexity
from planner.planner_builder import PlannerBuilder
from planner.query_analyzer import QueryAnalyzer
from routing.model_route import ModelRoute
from routing.model_router import ModelRouter
from routing.model_routing_validator import ModelRoutingValidator
from routing.model_target import ModelTarget


EXPECTED_TARGET_BY_COMPLEXITY = {
    Complexity.LOW: ModelTarget.LIGHTWEIGHT,
    Complexity.MEDIUM: ModelTarget.STANDARD,
    Complexity.HIGH: ModelTarget.ADVANCED,
}


PIPELINE_CASES = [
    ("What is Python?", Complexity.LOW),
    ("Explain Python decorators.", Complexity.MEDIUM),
    ("Design a system architecture for document search.", Complexity.HIGH),
]


def _build_plan(query: str):
    context = QueryAnalyzer.analyze(query)
    return PlannerBuilder.build(
        processing_goal=context.processing_goal,
        complexity=context.complexity,
        resource_requirements=context.resource_requirements,
        decision_trace=context.decision_trace,
    )


@pytest.mark.parametrize(("query", "expected_complexity"), PIPELINE_CASES)
def test_planner_to_model_router_pipeline(query, expected_complexity):
    plan = _build_plan(query)
    before = plan.to_dict()

    route = ModelRouter.route(plan)

    assert plan.complexity is expected_complexity
    assert plan.to_dict() == before
    assert isinstance(route, ModelRoute)
    assert route.target is EXPECTED_TARGET_BY_COMPLEXITY[plan.complexity]
    ModelRoutingValidator.validate_output(route)
    ModelRoutingValidator.validate_routing_invariant(plan, route)


@pytest.mark.parametrize(("query", "expected_complexity"), PIPELINE_CASES)
def test_planner_to_model_router_pipeline_is_deterministic(
    query,
    expected_complexity,
):
    first_plan = _build_plan(query)
    second_plan = _build_plan(query)

    first_route = ModelRouter.route(first_plan)
    second_route = ModelRouter.route(second_plan)

    assert first_plan.complexity is expected_complexity
    assert second_plan.complexity is expected_complexity
    assert first_plan.to_dict() == second_plan.to_dict()
    assert first_route == second_route
    assert first_route.to_dict() == second_route.to_dict()
