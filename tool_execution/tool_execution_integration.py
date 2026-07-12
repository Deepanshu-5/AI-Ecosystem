"""Deterministic orchestration from ToolRoute to ToolExecutionResult."""

from __future__ import annotations

from routing.tool_route import ToolRoute
from tool_execution.exceptions import ToolExecutionRuntimeError
from tool_execution.execution_validator import ExecutionValidator
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_execution_result import ToolExecutionResult
from tool_execution.tool_result import ToolResult


class ToolExecutionIntegration:
    """Execute exactly the semantic capabilities selected by ToolRoute."""

    def __init__(self, runtime_executor: RuntimeExecutor) -> None:
        """Establish the internal provider-independent runtime dependency."""
        self._runtime_executor = runtime_executor

    def execute(self, tool_route: ToolRoute) -> ToolExecutionResult:
        """Validate, execute in route order, validate, and return one result."""
        ExecutionValidator.validate_input(tool_route, self._runtime_executor)

        results: list[ToolResult] = []
        try:
            for capability in tool_route.capabilities:
                results.append(self._runtime_executor.execute(capability))
        except Exception as error:
            raise ToolExecutionRuntimeError(
                "Runtime invocation failed during tool execution."
            ) from error

        tool_execution_result = ToolExecutionResult(results=tuple(results))
        ExecutionValidator.validate_output(tool_execution_result, tool_route)
        return tool_execution_result
