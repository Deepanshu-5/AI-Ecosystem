from dataclasses import FrozenInstanceError

import pytest

from routing.tool_capability import ToolCapability
from tool_execution.tool_result import CURRENT_SCHEMA_VERSION, ToolResult


def test_tool_result_is_immutable_versioned_and_serializes_stably() -> None:
    result = ToolResult(
        capability=ToolCapability.KNOWLEDGE_ACCESS,
        payload={"items": ["Python"], "count": 1},
    )

    assert result.version == CURRENT_SCHEMA_VERSION
    assert result.to_dict() == {
        "capability": "knowledge_access",
        "payload": {"items": ["Python"], "count": 1},
        "version": 1,
    }
    assert list(result.to_dict()) == ["capability", "payload", "version"]
    with pytest.raises(FrozenInstanceError):
        result.payload = {}  # type: ignore[misc]


def test_tool_result_equality_and_replay_are_deterministic() -> None:
    first = ToolResult(ToolCapability.MEMORY_ACCESS, {"memory": "tea"})
    second = ToolResult(ToolCapability.MEMORY_ACCESS, {"memory": "tea"})

    assert first == second
    assert first.to_dict() == second.to_dict()
