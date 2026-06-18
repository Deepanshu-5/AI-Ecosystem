def is_valid_memory(
    memory: str
) -> bool:

    if not memory:
        return False

    memory = memory.strip()

    invalid_patterns = [
        "no conversation content",
        "summary: none",
        "conversation content not provided"
    ]

    lower_memory = memory.lower()

    for pattern in invalid_patterns:

        if pattern in lower_memory:
            return False

    if len(memory) < 20:
        return False

    return True