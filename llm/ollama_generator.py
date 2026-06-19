# llm/ollama_generator.py
import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)
    
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
    think=False,
    keep_alive="30m"
)


        content = response.message.content

        if "</think>" in content:
           content = content.split("</think>", 1)[1].strip()

        return content
    
