import sys
from pathlib import Path

from openai import chat

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from config.settings import (
    SUMMARY_MODEL
)

from llm.ollama_generator import (
    OllamaGenerator
)

generator = OllamaGenerator(
    SUMMARY_MODEL
)
def summarize_chat(
    chat_text: str
) -> str:

    prompt = f"""
Extract user memories.

A memory can be:

- A preference
- A favorite thing
- A goal
- A project
- A personal fact

Examples:

"My favorite database is ChromaDB."
→ Preference: ChromaDB

"I prefer local models."
→ Preference: Local models

"My goal is reducing token usage."
→ Goal: Reduce token usage

Rules:

1. Return one memory per line.
2. Do not explain.
3. Do not invent information.
4. If no memories exist, output exactly:

NO_MEMORY

Conversation:

{chat_text}
"""
    
    response = generator.generate(prompt)

    return response