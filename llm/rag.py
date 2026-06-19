from services.knowledge_service import search
from services.context_formatter import format_context
from llm.prompt_builder import build_prompt
from services.context_compressor import compress_context
from llm.generator_factory import GeneratorFactory
from memory.memory_service import (
    recall
)
from conversation_memory.session_memory import (
    get_session_context,
    process_message
)


def create_rag_prompt(
    question: str,
    session_id: str = "",
    top_k: int = 10,
    final_k: int = 2
):

    conversation_summary = ""
    recent_messages = ""

    if session_id:
        session_context = get_session_context(
            session_id
        )
        conversation_summary = session_context[
            "summary"
        ]
        recent_messages = session_context[
            "recent_messages"
        ]

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

    compressed_knowledge = compress_context(
        knowledge_context
    )

    compressed_memory = (
        compress_context(memory_context)
        if memory_context.strip()
        else ""
    )

    prompt = build_prompt(
        question=question,
        knowledge_context=compressed_knowledge,
        memory_context=compressed_memory,
        conversation_summary=conversation_summary,
        recent_messages=recent_messages
    )

    generator = GeneratorFactory.create(
        "ollama"
    )

    print("\n===== FINAL PROMPT =====\n")
    print(prompt)

    answer = generator.generate(
        prompt
    )

    if session_id:
        process_message(
            session_id,
            "user",
            question
        )
        process_message(
            session_id,
            "assistant",
            answer
        )

    return answer

