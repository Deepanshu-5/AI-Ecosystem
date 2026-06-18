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
    sentences = [
    s.strip()
    for s in consolidated_memory.split(".")
    if s.strip()
]

    if sentences:
     consolidated_memory = (
        sentences[0] + "."
    )

    return consolidated_memory


if __name__ == "__main__":

    memories = [
        "User is building an AI ecosystem using MCP and ChromaDB.",
        "The project uses RAG and memory compression.",
        "The goal is reducing token usage.",
        "Ollama and Qwen3 are used as the local LLM stack."
    ]

    result = consolidate_memories(
        memories
    )

    print(
        "\n===== CONSOLIDATED MEMORY =====\n"
    )

    print(result)