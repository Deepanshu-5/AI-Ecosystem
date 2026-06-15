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

Your task is to extract only the important long-term information.

Rules:

1. Remove greetings and casual discussion.
2. Remove repeated information.
3. Keep goals, decisions, preferences, project status, and important facts.
4. Write a concise summary.
5. Maximum 150 words.

Conversation:

{chat_text}

Summary:
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