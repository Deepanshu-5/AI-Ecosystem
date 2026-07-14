from __future__ import annotations

from typing import Any, Callable, Optional

from .lifecycle import LifecycleCoordinator
from .participation import ParticipationCoordinator
from .result import ControlPlaneResult

# Public contracts used only for typing clarity (treated as opaque)
from planner.execution_plan import ExecutionPlan


def run_control_plane(
    application_request: str,

    # The validated Planner public interface is represented by either a
    # prebuilt ExecutionPlan or a callable that returns one for the given
    # application_request. The orchestrator depends only on this validated
    # public interface supplied by the caller.
    execution_plan_or_callable: ExecutionPlan | Callable[[str], ExecutionPlan],

    # Validated subsystem public interfaces supplied via dependency injection.
    retriever_callable: Callable[[ExecutionPlan, str, Optional[str]], Any],
    budgeter_callable: Callable[[Any, str, int, int, Optional[dict]], Any],
    prompt_builder_callable: Callable[[Any], Any],
    model_route_resolver: Callable[[ExecutionPlan], Optional[Any]],
    tool_route_resolver: Callable[[ExecutionPlan], Optional[Any]],
    model_execution_callable: Callable[[Any, Any, Any], Any],
    tool_execution_callable: Callable[[Any], Any],

    # Provider-neutral runtime objects supplied by the caller when required.
    # The orchestrator never creates provider or infrastructure objects.
    generator: Any | None,

    # Budget parameters are passed through to Context Budgeting by the caller.
    total_budget: int,
    reserved_budget: int,
    category_caps: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> ControlPlaneResult:
    """Public entry point for one Control Plane execution.

    The function delegates lifecycle coordination to the Lifecycle Coordinator
    and participation coordination to the Participation Coordinator. All
    validated subsystem public interfaces and runtime/provider-neutral
    objects must be supplied by the caller (dependency injection). The
    orchestrator does not construct or own injected dependencies.

    This entry point is the single public boundary representing one Control
    Plane execution. It is stateless: any execution-specific state exists only
    for the lifetime of this call.
    """

    # Build ParticipationCoordinator with injected validated public interfaces
    participation = ParticipationCoordinator(
        execution_plan_or_callable=execution_plan_or_callable,
        retriever_callable=retriever_callable,
        budgeter_callable=budgeter_callable,
        prompt_builder_callable=prompt_builder_callable,
        model_route_resolver=model_route_resolver,
        tool_route_resolver=tool_route_resolver,
        model_execution_callable=model_execution_callable,
        tool_execution_callable=tool_execution_callable,
    )

    lifecycle = LifecycleCoordinator(participation)

    # Delegate lifecycle management and return composed ControlPlaneResult
    result = lifecycle.run(
        query=application_request,
        session_id=session_id,
        total_budget=total_budget,
        reserved_budget=reserved_budget,
        category_caps=category_caps,
        generator=generator,
    )

    return result
