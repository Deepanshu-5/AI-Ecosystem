# llm/ollama_generator.py

from ollama import chat
from llm.base_generator import BaseGenerator


class OllamaGenerator(
    BaseGenerator
):

    def generate(
        self,
        prompt: str
    ) -> str:

        response = chat(
            model="qwen3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            keep_alive="30m"
        )

        return response.message.content