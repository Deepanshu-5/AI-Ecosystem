import pytest

from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from tool_execution.exceptions import (
    ToolExecutionValidationError,
    UnsupportedToolRouteVersionError,
)
from tool_execution.execution_validator import ExecutionValidator
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_execution_result import ToolExecutionResult
from tool_execution.tool_result import ToolResult


class _RuntimeExecutor(RuntimeExecutor):
    def execute(self, capability: ToolCapability) -> ToolResult:
        return ToolResult(capability, {"value": capability.value})


def _route() -> ToolRoute:
    return ToolRoute(
        capabilities=(ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.MEMORY_ACCESS),
        reason="valid route",
    )


def _result() -> ToolExecutionResult:
    return ToolExecutionResult(
        results=(
            ToolResult(ToolCapability.KNOWLEDGE_ACCESS, {"value": "knowledge"}),
            ToolResult(ToolCapability.MEMORY_ACCESS, {"value": "memory"}),
        )
    )


def test_valid_execution_boundary_and_result_are_accepted() -> None:
    ExecutionValidator.validate_input(_route(), _RuntimeExecutor())
    ExecutionValidator.validate_output(_result(), _route())


def test_invalid_tool_route_and_missing_runtime_are_rejected() -> None:
    with pytest.raises(ToolExecutionValidationError, match="expected ToolRoute"):
        ExecutionValidator.validate_input("not a route", _RuntimeExecutor())  # type: ignore[arg-type]
    with pytest.raises(ToolExecutionValidationError, match="expected RuntimeExecutor"):
        ExecutionValidator.validate_input(_route(), object())  # type: ignore[arg-type]


def test_unsupported_route_version_is_rejected_by_its_domain_exception() -> None:
    route = _route()
    object.__setattr__(route, "version", 2)

    with pytest.raises(UnsupportedToolRouteVersionError, match="unsupported ToolRoute"):
        ExecutionValidator.validate_input(route, _RuntimeExecutor())


def test_duplicate_and_noncanonical_capabilities_are_rejected() -> None:
    duplicate = _route()
    object.__setattr__(
        duplicate,
        "capabilities",
        (ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.KNOWLEDGE_ACCESS),
    )
    with pytest.raises(ToolExecutionValidationError, match="duplicate"):
        ExecutionValidator.validate_input(duplicate, _RuntimeExecutor())

    unordered = _route()
    object.__setattr__(
        unordered,
        "capabilities",
        (ToolCapability.MEMORY_ACCESS, ToolCapability.KNOWLEDGE_ACCESS),
    )
    with pytest.raises(ToolExecutionValidationError, match="canonical order"):
        ExecutionValidator.validate_input(unordered, _RuntimeExecutor())


def test_invalid_output_payload_and_order_are_rejected() -> None:
    invalid_payload = _result()
    object.__setattr__(invalid_payload.results[0], "payload", {"bad": object()})
    with pytest.raises(ToolExecutionValidationError, match="Serializable"):
        ExecutionValidator.validate_output(invalid_payload, _route())

    unordered = ToolExecutionResult(results=tuple(reversed(_result().results)))
    with pytest.raises(ToolExecutionValidationError, match="match ToolRoute ordering"):
        ExecutionValidator.validate_output(unordered, _route())
