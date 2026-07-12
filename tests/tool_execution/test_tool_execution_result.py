from dataclasses import FrozenInstanceError

import pytest

from routing.tool_capability import ToolCapability
from tool_execution.tool_execution_result import (
    CURRENT_SCHEMA_VERSION,
    ToolExecutionResult,
)
from tool_execution.tool_result import ToolResult


def test_empty_tool_execution_result_is_immutable_and_versioned() -> None:
    result = ToolExecutionResult(results=())

    assert result.version == CURRENT_SCHEMA_VERSION
    assert result.to_dict() == {"results": [], "version": 1}
    with pytest.raises(FrozenInstanceError):
        result.results = ()  # type: ignore[misc]


def test_tool_execution_result_preserves_order_and_serialization() -> None:
    results = (
        ToolResult(ToolCapability.KNOWLEDGE_ACCESS, {"value": "knowledge"}),
        ToolResult(ToolCapability.MEMORY_ACCESS, {"value": "memory"}),
    )
    execution_result = ToolExecutionResult(results=results)

    assert execution_result.results == results
    assert execution_result.to_dict() == {
        "results": [result.to_dict() for result in results],
        "version": 1,
    }
    assert execution_result == ToolExecutionResult(results=results)
