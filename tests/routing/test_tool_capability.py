from routing.tool_capability import ToolCapability


def test_tool_capability_has_exact_members():
    assert tuple(ToolCapability) == (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    )


def test_tool_capability_has_exact_values():
    assert ToolCapability.KNOWLEDGE_ACCESS.value == "knowledge_access"
    assert ToolCapability.MEMORY_ACCESS.value == "memory_access"
    assert ToolCapability.SESSION_ACCESS.value == "session_access"


def test_tool_capability_values_are_unique():
    values = [capability.value for capability in ToolCapability]

    assert len(values) == len(set(values))
