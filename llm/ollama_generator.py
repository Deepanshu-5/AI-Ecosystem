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
from config.settings import (
    CHAT_MODEL
)

class OllamaGenerator(
    BaseGenerator
):

    def __init__(
        self,
        model_name=CHAT_MODEL
    ):
        self.model_name = model_name

    def generate(
        self,
        prompt: str
    ) -> str:


        print(
            f"[MODEL] {self.model_name}"
        )

        import time

        start = time.perf_counter()

        response = chat(
    model=self.model_name,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    think=False,
    keep_alive="20m",
    options={
        "temperature": 0,
        "top_p": 1,
        "seed": 42
    }
)  
        
        elapsed = time.perf_counter() - start

        print(
    f"[OLLAMA CALL] {elapsed:.2f}s"
)


        content = response.message.content

        if "</think>" in content:
            content = (
                content
                .split("</think>", 1)[1]
                .strip()
            )

        return content