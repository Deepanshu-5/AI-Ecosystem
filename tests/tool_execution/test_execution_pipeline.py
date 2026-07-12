from planner.planner_builder import PlannerBuilder
from planner.query_analyzer import QueryAnalyzer
from routing.tool_router import ToolRouter
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_execution_integration import ToolExecutionIntegration
from tool_execution.tool_result import ToolResult


class _RuntimeExecutor(RuntimeExecutor):
    def __init__(self) -> None:
        self.received = []

    def execute(self, capability) -> ToolResult:
        self.received.append(capability)
        return ToolResult(capability, {"value": capability.value})


def _route_for(query: str):
    context = QueryAnalyzer.analyze(query)
    plan = PlannerBuilder.build(
        processing_goal=context.processing_goal,
        complexity=context.complexity,
        resource_requirements=context.resource_requirements,
        decision_trace=context.decision_trace,
    )
    return ToolRouter.route(plan)


def test_planner_tool_router_and_execution_pipeline_preserves_route() -> None:
    route = _route_for("What do you know and remember from earlier?")
    before = route.to_dict()
    runtime = _RuntimeExecutor()

    result = ToolExecutionIntegration(runtime).execute(route)

    assert runtime.received == list(route.capabilities)
    assert [item.capability for item in result.results] == list(route.capabilities)
    assert route.to_dict() == before
    assert result == ToolExecutionIntegration(_RuntimeExecutor()).execute(_route_for("What do you know and remember from earlier?"))
