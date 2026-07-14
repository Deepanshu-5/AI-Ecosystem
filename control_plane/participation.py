from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

# Treat domain objects from validated subsystems as opaque immutable contracts
from planner.execution_plan import ExecutionPlan
from retriever.retrieved_context import RetrievedContext
from budgeting.budgeted_context import BudgetedContext
from prompt_builder.prompt import Prompt
from routing.model_route import ModelRoute
from routing.tool_route import ToolRoute
from model_execution.model_response import ModelResponse
from tool_execution.tool_execution_result import ToolExecutionResult


class ParticipationCoordinator:
    """Participation Coordinator component.

    Responsibility:
        Coordinate validated subsystem participation for one Control Plane
        execution. This component invokes only the validated public interfaces
        supplied by the caller. It never constructs subsystem internals, does
        not perform semantic interpretation, and does not implement execution
        policy.

    The coordinator accepts callables or prebuilt immutable objects representing
    validated subsystem public interfaces. Concrete method names and object
    shapes are the responsibility of the caller; the coordinator treats
    injected interfaces as opaque callables.
    """

    def __init__(
        self,
        execution_plan_or_callable: ExecutionPlan | Callable[[str], ExecutionPlan],
        retriever_callable: Callable[[ExecutionPlan, str, Optional[str]], RetrievedContext],
        budgeter_callable: Callable[[RetrievedContext, str, int, int, Optional[dict]], BudgetedContext],
        prompt_builder_callable: Callable[[BudgetedContext], Prompt],
        model_route_resolver: Callable[[ExecutionPlan], Optional[ModelRoute]],
        tool_route_resolver: Callable[[ExecutionPlan], Optional[ToolRoute]],
        model_execution_callable: Callable[[Prompt, ModelRoute, Any], ModelResponse],
        tool_execution_callable: Callable[[ToolRoute], ToolExecutionResult],
    ) -> None:
        # Dependencies are injected; this component does not own their lifetime
        self._execution_plan_or_callable = execution_plan_or_callable
        self._retriever = retriever_callable
        self._budgeter = budgeter_callable
        self._prompt_builder = prompt_builder_callable
        self._model_route_resolver = model_route_resolver
        self._tool_route_resolver = tool_route_resolver
        self._model_executor = model_execution_callable
        self._tool_executor = tool_execution_callable

    def coordinate(
        self,
        query: str,
        session_id: Optional[str],
        total_budget: int,
        reserved_budget: int,
        category_caps: Optional[dict] = None,
        generator: Any | None = None,
    ) -> Tuple[ModelResponse | None, ToolExecutionResult | None]:
        """Coordinate participation for one execution.

        Parameters are passed through from the lifecycle coordinator. Subsystem
        outputs are treated as opaque immutable contracts and returned
        unchanged.

        Returns a 2-tuple: (model_response|None, tool_execution_result|None)
        """
        # Resolve ExecutionPlan: allow caller to supply either a prebuilt
        # ExecutionPlan or a callable that accepts the query and returns one.
        if isinstance(self._execution_plan_or_callable, ExecutionPlan):
            execution_plan = self._execution_plan_or_callable
        elif callable(self._execution_plan_or_callable):
            execution_plan = self._execution_plan_or_callable(query)
        else:
            raise TypeError("execution_plan_or_callable must be ExecutionPlan or callable")

        # 1. Retrieval
        retrieved_context = self._retriever(execution_plan, query, session_id)

        # 2. Budgeting — caller supplies budget values to avoid introducing policy
        budgeted_context = self._budgeter(retrieved_context, query, total_budget, reserved_budget, category_caps)

        # 3. Prompt construction
        prompt = self._prompt_builder(budgeted_context)

        # 4. Resolve routes
        model_route = self._model_route_resolver(execution_plan)
        tool_route = self._tool_route_resolver(execution_plan)

        model_response = None
        tool_result = None

        # 5. Invoke model branch if a route exists
        if model_route is not None:
            if generator is None:
                raise ValueError("Model route resolved but no provider-neutral generator supplied")
            model_response = self._model_executor(prompt, model_route, generator)

        # 6. Invoke tool branch if a route exists
        if tool_route is not None:
            tool_result = self._tool_executor(tool_route)

        return model_response, tool_result
