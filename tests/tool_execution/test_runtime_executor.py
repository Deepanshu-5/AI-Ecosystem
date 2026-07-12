import pytest

from routing.tool_capability import ToolCapability
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_result import ToolResult


class _RuntimeExecutor(RuntimeExecutor):
    def __init__(self) -> None:
        self.received: list[ToolCapability] = []

    def execute(self, capability: ToolCapability) -> ToolResult:
        self.received.append(capability)
        return ToolResult(capability, {"value": capability.value})


class _FailingRuntimeExecutor(RuntimeExecutor):
    def execute(self, capability: ToolCapability) -> ToolResult:
        raise RuntimeError("runtime failure")


def test_runtime_executor_contract_forwards_capability_and_result() -> None:
    runtime = _RuntimeExecutor()

    result = runtime.execute(ToolCapability.SESSION_ACCESS)

    assert runtime.received == [ToolCapability.SESSION_ACCESS]
    assert result == ToolResult(ToolCapability.SESSION_ACCESS, {"value": "session_access"})


def test_runtime_executor_failure_propagates_from_boundary() -> None:
    with pytest.raises(RuntimeError, match="runtime failure"):
        _FailingRuntimeExecutor().execute(ToolCapability.KNOWLEDGE_ACCESS)
