import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from llm.ollama_generator import (
    OllamaGenerator
)

def summarize_chat(
    chat_text: str
) -> str:

    generator = OllamaGenerator()

    prompt = f"""
You are a memory compression system.

Create exactly ONE long-term memory.

Rules:

1. Keep only durable information.
2. Remove repetition.
3. Merge similar facts.
4. Produce ONE paragraph only.
5. Do not produce multiple summaries.
6. Do not repeat the same idea in different wording.
7. Maximum 60 words.
8. Output only the final memory.

Conversation:

{chat_text}

Memory:
"""

    return generator.generate(
        prompt
    )
if __name__ == "__main__":

    chat = """
User is building an AI ecosystem.

The project uses:
- ChromaDB
- MCP
- Claude Desktop
- Ollama

Main goal:
Reduce token usage through RAG and memory compression.
"""

    summary = summarize_chat(
        chat
    )

    print(
        "\nSUMMARY:\n"
    )

    print(
        summary
    )