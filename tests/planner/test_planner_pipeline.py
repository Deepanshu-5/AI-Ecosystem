from planner.planner_builder import PlannerBuilder
from planner.query_analyzer import QueryAnalyzer


def test_complete_planner_pipeline():
    context = QueryAnalyzer.analyze(
        "Explain what Python decorators are."
    )

    plan = PlannerBuilder.build(
        processing_goal=context.processing_goal,
        complexity=context.complexity,
        resource_requirements=context.resource_requirements,
        decision_trace=context.decision_trace,
    )

    assert plan.processing_goal == context.processing_goal
    assert plan.complexity == context.complexity
    assert plan.resource_requirements == context.resource_requirements
    assert plan.decision_trace == context.decision_trace