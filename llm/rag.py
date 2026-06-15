from typer import prompt

from services.knowledge_service import search
from services.context_formatter import format_context
from llm.prompt_builder import build_prompt
from services.context_compressor import compress_context
from llm.generator_factory import GeneratorFactory
from memory.memory_service import (
    recall
)
def create_rag_prompt(
    question: str,
    top_k: int =10,
    final_k: int = 2
):

   ranked = search(
    question,
    top_k=top_k,
    final_k=final_k
)

   
   knowledge_context = format_context(
    ranked
)

   memories = recall(
    question,
    top_k=top_k
)

   memory_context = "\n".join(
    memories
)

   context = f"""
MEMORIES:

{memory_context}

KNOWLEDGE:

{knowledge_context}
"""

   compressed_context = compress_context(
    context
)

   prompt = build_prompt(
    question,
    compressed_context
)
   generator = GeneratorFactory.create(
    "ollama"
)
   print("\n===== FINAL PROMPT =====\n")
   print(prompt)
   answer = generator.generate(
    prompt
)

   return answer

