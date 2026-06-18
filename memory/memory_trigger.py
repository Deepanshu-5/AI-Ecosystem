import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)
from memory.memory_manager import (
    process_conversation
)

MESSAGE_THRESHOLD = 10


class MemoryTrigger:

    def __init__(self):

        self.messages = []

    def add_message(
        self,
        message: str
    ):

        self.messages.append(
            message
        )

        if len(self.messages) >= MESSAGE_THRESHOLD:

            conversation = "\n".join(
                self.messages
            )

            summary = process_conversation(
                conversation
            )

            self.messages.clear()

            return summary

        return None
if __name__ == "__main__":

    trigger = MemoryTrigger()

    messages = [
        "User is building an AI ecosystem.",
        "The system uses ChromaDB.",
        "The project uses MCP.",
        "Claude Desktop is integrated.",
        "Ollama is being used.",
        "Qwen3 is the local LLM.",
        "The goal is reducing token usage.",
        "The project uses memory compression.",
        "The project uses RAG.",
        "The user wants long-term memory."
    ]

    for msg in messages:

        result = trigger.add_message(
            msg
        )

        if result:

            print(
                "\nSUMMARY:\n"
            )

            print(
                result
            ) 