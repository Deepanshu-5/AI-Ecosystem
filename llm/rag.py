from services.knowledge_service import search
from services.context_formatter import format_context
from llm.prompt_builder import build_prompt
from services.context_compressor import compress_context

def create_rag_prompt(
    question: str,
    top_k: int = 10,
    final_k: int = 2
):

   ranked = search(
    question,
    top_k
)

   context = format_context(
    ranked
)

   compressed_context = compress_context(
    context
)

   prompt = build_prompt(
    question,
    compressed_context
)

   return prompt