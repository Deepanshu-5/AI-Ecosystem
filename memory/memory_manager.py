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

from memory.memory_service import (
    remember
)


def process_conversation(
    chat_text: str
):

    summary = summarize_chat(
        chat_text
    )

    remember(
        summary
    )

    return summary
if __name__ == "__main__":

    conversation = """
User is building an AI ecosystem.

Uses:
- ChromaDB
- MCP
- Claude Desktop
- Ollama

Goal:
Reduce token usage using RAG and memory compression.
"""

    summary = process_conversation(
        conversation
    )

    print(
        summary
    )