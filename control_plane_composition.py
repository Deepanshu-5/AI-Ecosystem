"""
Example application composition root for wiring validated subsystem public
interfaces and provider-neutral runtime objects.

This module is intentionally located outside the control_plane package and is
not part of the Control Plane subsystem or the frozen architecture. Production
applications may use a different composition root. It exists solely as an
example of how dependency creation and lifetime ownership remain outside the
Control Plane package.

It constructs validated subsystem instances using public constructors and
supplies their public interfaces to the Control Plane Orchestrator via
dependency injection. The Control Plane package does not own any created
dependencies' lifetimes.
"""
from typing import Callable, Optional

from control_plane import run_control_plane

# Planner internals used here only to construct a validated ExecutionPlan
from planner.query_analyzer import QueryAnalyzer
from planner.planner_builder import PlannerBuilder

# Validated subsystem public interfaces / constructors
from integration.integrations.retriever_integration import RetrieverIntegration
from budgeting.context_budgeter import ContextBudgeter
from prompt_builder.prompt_builder import PromptBuilder
from routing.model_router import ModelRouter
from routing.tool_router import ToolRouter
from model_execution.model_execution_integration import ModelExecutionIntegration
from tool_execution.tool_execution_integration import ToolExecutionIntegration
from llm.placeholder_generator import PlaceholderGenerator
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_result import ToolResult
from routing.tool_capability import ToolCapability

from planner.processing_goal import ProcessingGoal
from planner.complexity import Complexity
from planner.resource_requirements import ResourceRequirements
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan


class _SimpleRuntime(RuntimeExecutor):
    """A trivial runtime executor used by example composition.

    This example executor is provider-neutral and returns a ToolResult with
    a simple payload. It is provided here only as an example; production
    compositions must supply real runtime executors owned outside the
    Control Plane.
    """

    def execute(self, capability: ToolCapability) -> ToolResult:
        return ToolResult(capability, {"value": capability.value})


def build_and_run_example(query: str) -> None:
    # 1. Build an ExecutionPlan using Planner internals (composition root only)
    planning_context = QueryAnalyzer.analyze(query)
    execution_plan = PlannerBuilder.build(
        planning_context.processing_goal,
        planning_context.complexity,
        planning_context.resource_requirements,
        planning_context.decision_trace,
    )

    # 2. Construct validated subsystem public interfaces
    retriever = RetrieverIntegration()
    budgeter = ContextBudgeter()
    prompt_builder = PromptBuilder()
    model_router = ModelRouter()
    tool_router = ToolRouter()

    model_executor = ModelExecutionIntegration()
    tool_runtime = _SimpleRuntime()
    tool_execution_integration = ToolExecutionIntegration(tool_runtime)

    # 3. Provider-neutral generator (example)
    generator = PlaceholderGenerator()

    # 4. Run the Control Plane execution via the public orchestrator boundary
    result = run_control_plane(
        application_request=query,
        execution_plan_or_callable=execution_plan,
        retriever_callable=retriever.build,
        budgeter_callable=budgeter.budget,
        prompt_builder_callable=prompt_builder.build,
        model_route_resolver=model_router.resolve,
        tool_route_resolver=tool_router.resolve,
        model_execution_callable=model_executor.execute,
        tool_execution_callable=tool_execution_integration.execute,
        generator=generator,
        total_budget=1024,
        reserved_budget=128,
        category_caps=None,
        session_id=None,
    )

    print("Control Plane Result:")
    print(result)


if __name__ == "__main__":
    build_and_run_example("What is the capital of France?")
