from dataclasses import FrozenInstanceError

import pytest

from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from tool_execution.exceptions import ToolExecutionRuntimeError, ToolExecutionValidationError
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_execution_integration import ToolExecutionIntegration
from tool_execution.tool_result import ToolResult


class _RecordingRuntime(RuntimeExecutor):
    def __init__(self) -> None:
        self.capabilities: list[ToolCapability] = []

    def execute(self, capability: ToolCapability) -> ToolResult:
        self.capabilities.append(capability)
        return ToolResult(capability, {"value": capability.value})


class _FailingRuntime(_RecordingRuntime):
    def execute(self, capability: ToolCapability) -> ToolResult:
        super().execute(capability)
        raise RuntimeError("provider failure")


def _route(capabilities: tuple[ToolCapability, ...]) -> ToolRoute:
    return ToolRoute(capabilities=capabilities, reason="valid route")


def test_empty_route_returns_empty_result_without_runtime_execution() -> None:
    runtime = _RecordingRuntime()

    result = ToolExecutionIntegration(runtime).execute(_route(()))

    assert result.results == ()
    assert runtime.capabilities == []


@pytest.mark.parametrize(
    "capability",
    [
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    ],
)
def test_single_capability_execution_preserves_semantic_capability(capability) -> None:
    runtime = _RecordingRuntime()

    result = ToolExecutionIntegration(runtime).execute(_route((capability,)))

    assert runtime.capabilities == [capability]
    assert result.results == (ToolResult(capability, {"value": capability.value}),)


def test_execution_preserves_order_and_does_not_mutate_route() -> None:
    capabilities = (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    )
    route = _route(capabilities)
    before = route.to_dict()
    runtime = _RecordingRuntime()

    result = ToolExecutionIntegration(runtime).execute(route)

    assert runtime.capabilities == list(capabilities)
    assert tuple(item.capability for item in result.results) == capabilities
    assert route.to_dict() == before
    with pytest.raises(FrozenInstanceError):
        result.results = ()  # type: ignore[misc]


def test_runtime_failure_is_translated_and_execution_stops() -> None:
    runtime = _FailingRuntime()
    route = _route((ToolCapability.KNOWLEDGE_ACCESS, ToolCapability.MEMORY_ACCESS))

    with pytest.raises(ToolExecutionRuntimeError, match="Runtime invocation failed") as error:
        ToolExecutionIntegration(runtime).execute(route)

    assert isinstance(error.value.__cause__, RuntimeError)
    assert runtime.capabilities == [ToolCapability.KNOWLEDGE_ACCESS]


def test_invalid_runtime_output_is_rejected_without_partial_result() -> None:
    class _InvalidRuntime(RuntimeExecutor):
        def execute(self, capability: ToolCapability) -> ToolResult:
            return ToolResult(ToolCapability.MEMORY_ACCESS, {"value": "wrong"})

    with pytest.raises(ToolExecutionValidationError, match="match ToolRoute ordering"):
        ToolExecutionIntegration(_InvalidRuntime()).execute(
            _route((ToolCapability.KNOWLEDGE_ACCESS,))
        )
