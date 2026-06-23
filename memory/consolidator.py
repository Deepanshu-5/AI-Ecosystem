import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.chat_summarizer import (
    summarize_chat
)


def consolidate_memories(
    memories: list[str]
) -> str:

    if not memories:
        return ""

    memory_text = "\n\n".join(
        memories
    )

    consolidated_memory = summarize_chat(
        memory_text
    )
    consolidated_memory = (
    consolidated_memory
    .replace("\n", " ")
    .strip()
)

    return consolidated_memory


