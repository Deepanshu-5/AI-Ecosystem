import sys
from dataclasses import FrozenInstanceError, asdict
from pathlib import Path

# Ensure repository root is discoverable when tests run in isolation
ROOT = str(Path(__file__).resolve().parents[2])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from control_plane import run_control_plane, ControlPlaneResult
from control_plane.lifecycle import LifecycleCoordinator, LifecycleState
from control_plane.participation import ParticipationCoordinator

from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.complexity import Complexity
from planner.resource_requirements import ResourceRequirements
from planner.decision_trace import DecisionTrace

from retriever.knowledge_context import KnowledgeContext
from retriever.memory_context import MemoryContext
from retriever.session_context import SessionContext
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budgeted_context import BudgetedContext
from prompt_builder.prompt import Prompt
from routing.model_route import ModelRoute
from routing.model_target import ModelTarget
from model_execution.model_response import ModelResponse
from tool_execution.tool_execution_result import ToolExecutionResult
from tool_execution.tool_result import ToolResult
from routing.tool_capability import ToolCapability


# Helper: construct minimal ExecutionPlan without using Planner builders
def _make_execution_plan() -> ExecutionPlan:
    processing_goal = ProcessingGoal.GENERAL
    complexity = Complexity.LOW
    resource_requirements = ResourceRequirements(knowledge=False, memory=False, session=False)
    decision_trace = DecisionTrace(
        processing_goal_reason="test",
        complexity_reason="test",
        resource_requirements_reason="test",
    )
    return ExecutionPlan(
        processing_goal=processing_goal,
        complexity=complexity,
        resource_requirements=resource_requirements,
        decision_trace=decision_trace,
    )


# Minimal stub implementations for validated subsystem public interfaces

def _stub_retriever(execution_plan, query: str, session_id: str | None):
    knowledge = KnowledgeContext.empty()
    memory = MemoryContext.empty()
    session = SessionContext.empty()
    metadata = RetrievalMetadata(
        knowledge_count=0,
        memory_count=0,
        session_count=0,
        knowledge_latency_ms=0,
        memory_latency_ms=0,
        session_latency_ms=0,
        total_latency_ms=0,
    )
    return RetrievedContext(knowledge=knowledge, memory=memory, session=session, metadata=metadata)


def _stub_budgeter(retrieved_context, query: str, total: int, reserved: int, category_caps=None):
    metadata = BudgetMetadata(
        total_budget=total,
        reserved_tokens=reserved,
        query_tokens=0,
        context_budget=0,
        used_context_tokens=0,
        remaining_tokens=0,
        knowledge_tokens=0,
        memory_tokens=0,
        session_tokens=0,
    )
    return BudgetedContext(
        knowledge=retrieved_context.knowledge,
        memory=retrieved_context.memory,
        session=retrieved_context.session,
        metadata=metadata,
        effective_query=query,
    )


def _stub_prompt_builder(budgeted_context):
    return Prompt(content=budgeted_context.effective_query)


def _model_route_resolver(execution_plan):
    return None


def _tool_route_resolver(execution_plan):
    return None


def _model_executor(prompt, model_route, generator):
    # Return a deterministic ModelResponse
    return ModelResponse(content="response")


def _tool_executor(tool_route):
    # Return an empty ToolExecutionResult
    return ToolExecutionResult(results=())


def test_run_control_plane_stateless_and_returns_control_plane_result():
    plan = _make_execution_plan()

    result = run_control_plane(
        application_request="hello",
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=_model_route_resolver,
        tool_route_resolver=_tool_route_resolver,
        model_execution_callable=_model_executor,
        tool_execution_callable=_tool_executor,
        generator=None,
        total_budget=256,
        reserved_budget=64,
        category_caps=None,
        session_id=None,
    )

    assert isinstance(result, ControlPlaneResult)
    assert result.model_response is None
    assert result.tool_execution_result is None

    # Call again to ensure statelessness (no exception, same outcome)
    result2 = run_control_plane(
        application_request="hello",
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=_model_route_resolver,
        tool_route_resolver=_tool_route_resolver,
        model_execution_callable=_model_executor,
        tool_execution_callable=_tool_executor,
        generator=None,
        total_budget=256,
        reserved_budget=64,
        category_caps=None,
        session_id=None,
    )

    assert result2 == result


def test_run_control_plane_with_model_branch_only():
    plan = _make_execution_plan()

    def model_route_resolver(execution_plan):
        return ModelRoute(target=ModelTarget.STANDARD, reason="test")

    def tool_route_resolver(execution_plan):
        return None

    class _Gen:
        def generate(self, prompt_content: str) -> str:
            return "model-only"

    def model_executor(prompt, model_route, generator):
        return ModelResponse(content=generator.generate(prompt.content))

    result = run_control_plane(
        application_request="query",
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=model_route_resolver,
        tool_route_resolver=tool_route_resolver,
        model_execution_callable=model_executor,
        tool_execution_callable=_tool_executor,
        generator=_Gen(),
        total_budget=256,
        reserved_budget=64,
        category_caps=None,
        session_id=None,
    )

    assert result.model_response is not None
    assert result.model_response.content == "model-only"
    assert result.tool_execution_result is None


def test_run_control_plane_with_tool_branch_only():
    plan = _make_execution_plan()

    def model_route_resolver(execution_plan):
        return None

    def tool_route_resolver(execution_plan):
        from routing.tool_route import ToolRoute

        return ToolRoute(capabilities=(ToolCapability.KNOWLEDGE_ACCESS,), reason="test")

    def tool_executor(tool_route):
        from tool_execution.tool_result import ToolResult

        return ToolExecutionResult(results=(ToolResult(ToolCapability.KNOWLEDGE_ACCESS, {"value": "ok"}),))

    result = run_control_plane(
        application_request="query",
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=model_route_resolver,
        tool_route_resolver=tool_route_resolver,
        model_execution_callable=_model_executor,
        tool_execution_callable=tool_executor,
        generator=None,
        total_budget=256,
        reserved_budget=64,
        category_caps=None,
        session_id=None,
    )

    assert result.model_response is None
    assert result.tool_execution_result is not None
    assert len(result.tool_execution_result.results) == 1


def test_run_control_plane_missing_injected_dependency_raises_type_error():
    plan = _make_execution_plan()

    with pytest.raises(TypeError):
        run_control_plane(
            application_request="query",
            execution_plan_or_callable=plan,
            retriever_callable=_stub_retriever,
            budgeter_callable=_stub_budgeter,
            prompt_builder_callable=None,
            model_route_resolver=_model_route_resolver,
            tool_route_resolver=_tool_route_resolver,
            model_execution_callable=_model_executor,
            tool_execution_callable=_tool_executor,
            generator=None,
            total_budget=256,
            reserved_budget=64,
            category_caps=None,
            session_id=None,
        )


def test_run_control_plane_missing_generator_when_model_route_exists_raises_value_error():
    plan = _make_execution_plan()

    def model_route_resolver(execution_plan):
        return ModelRoute(target=ModelTarget.STANDARD, reason="test")

    with pytest.raises(ValueError, match="Model route resolved but no provider-neutral generator supplied"):
        run_control_plane(
            application_request="query",
            execution_plan_or_callable=plan,
            retriever_callable=_stub_retriever,
            budgeter_callable=_stub_budgeter,
            prompt_builder_callable=_stub_prompt_builder,
            model_route_resolver=model_route_resolver,
            tool_route_resolver=_tool_route_resolver,
            model_execution_callable=_model_executor,
            tool_execution_callable=_tool_executor,
            generator=None,
            total_budget=256,
            reserved_budget=64,
            category_caps=None,
            session_id=None,
        )


def test_lifecycle_coordinator_invalid_transition_raises_runtime_error():
    plan = _make_execution_plan()
    participation = ParticipationCoordinator(
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=_model_route_resolver,
        tool_route_resolver=_tool_route_resolver,
        model_execution_callable=_model_executor,
        tool_execution_callable=_tool_executor,
    )
    coordinator = LifecycleCoordinator(participation)
    coordinator._enter_state(LifecycleState.EXECUTION_COORDINATING)
    with pytest.raises(RuntimeError, match="Invalid lifecycle transition"):
        coordinator._enter_state(LifecycleState.EXECUTION_REQUESTED)


def test_control_plane_result_is_immutable():
    result = ControlPlaneResult(model_response=None, tool_execution_result=None)
    with pytest.raises(FrozenInstanceError):
        result.version = 2


def test_control_plane_result_deterministic_serialization():
    result = ControlPlaneResult(model_response=None, tool_execution_result=None)
    first_serialization = asdict(result)
    second_serialization = asdict(result)
    assert first_serialization == second_serialization
    assert first_serialization == {"model_response": None, "tool_execution_result": None, "version": 1}


def test_run_control_plane_with_model_and_tool_branches():
    plan = _make_execution_plan()

    def model_route_resolver(execution_plan):
        return ModelRoute(target=ModelTarget.STANDARD, reason="test")

    def tool_route_resolver(execution_plan):
        # Construct a ToolRoute with one capability
        from routing.tool_route import ToolRoute

        return ToolRoute(capabilities=(ToolCapability.KNOWLEDGE_ACCESS,), reason="test")

    # model executor uses generator, provide dummy generator
    class _Gen:
        def generate(self, prompt_content: str) -> str:
            return "hello-model"

    def model_executor(prompt, model_route, generator):
        return ModelResponse(content=generator.generate(prompt.content))

    # Tool executor: produce one ToolResult in a ToolExecutionResult
    def tool_executor(tool_route):
        from tool_execution.tool_result import ToolResult
        return ToolExecutionResult(results=(ToolResult(ToolCapability.KNOWLEDGE_ACCESS, {"value": "ok"}),))

    result = run_control_plane(
        application_request="query",
        execution_plan_or_callable=plan,
        retriever_callable=_stub_retriever,
        budgeter_callable=_stub_budgeter,
        prompt_builder_callable=_stub_prompt_builder,
        model_route_resolver=model_route_resolver,
        tool_route_resolver=tool_route_resolver,
        model_execution_callable=model_executor,
        tool_execution_callable=tool_executor,
        generator=_Gen(),
        total_budget=256,
        reserved_budget=64,
        category_caps=None,
        session_id=None,
    )

    assert result.model_response is not None
    assert result.model_response.content == "hello-model"
    assert result.tool_execution_result is not None
    assert len(result.tool_execution_result.results) == 1
