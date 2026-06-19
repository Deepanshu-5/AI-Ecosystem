import time
from ollama import chat

start = time.perf_counter()

response = chat(
    model="qwen3:4b",
    messages=[
        {
            "role":"user",
            "content":"Say hello."
        }
    ]
)

print(response.message.content)

print(
    time.perf_counter() - start
)