from services.knowledge_service import search
from services.context_formatter import format_context
from llm.prompt_builder import build_prompt
from services.context_budgeter import get_budgeter
from observability.metrics_logger import log_query_metrics
import time
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
    overall_start = time.perf_counter()
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

    retrieval_start = time.perf_counter()
    

    ranked = search(
    question,
    top_k=top_k,
    final_k=final_k
)

    retrieval_latency = time.perf_counter() - retrieval_start
    print(
    f"[RETRIEVAL] "
    f"{retrieval_latency:.2f}s"
)

    knowledge_context = format_context(
        ranked
)

    

    start = time.time()

#     memories = recall(
#     question,
#     top_k=top_k
# )  
    memory_start = time.perf_counter()

    memories = recall(
    question,
    top_k=1
)

    memory_latency = time.perf_counter() - memory_start
    print(
    f"[MEMORY] "
    f"{memory_latency:.2f}s"
)


    memory_context = "\n".join(
        memories
    )
    budgeter_start = time.perf_counter()

    budgeter = get_budgeter()
    budget_result = budgeter.build_context(
        question=question,
        knowledge_context=knowledge_context,
        memory_context=memory_context,
        conversation_summary=conversation_summary,
        recent_messages=recent_messages,
    )
    budget_latency = time.perf_counter() - budgeter_start
    print(
        f"[BUDGETING] "
        f"{budget_latency:.2f}s"
    )
    print(budget_result["metrics"].report())

    prompt_start = time.perf_counter()
    prompt = build_prompt(
        question=question,
        knowledge_context=budget_result["knowledge_context"],
        memory_context=budget_result["memory_context"],
        conversation_summary=budget_result["conversation_summary"],
        recent_messages=budget_result["recent_messages"],
    )
    prompt_build_latency = time.perf_counter() - prompt_start
    print(
    f"[PROMPT BUILD] "
    f"{prompt_build_latency:.2f}s"
)

    from config.settings import (
    CHAT_MODEL
)

    from llm.ollama_generator import (
    OllamaGenerator
)   
    generator = OllamaGenerator(
    CHAT_MODEL
)
    import os
    if os.getenv("RAG_DEBUG"):
     print("\n===== FINAL PROMPT =====\n")
     print(prompt)
    
    from shared.token_counter import (
    count_tokens
)

    token_count = count_tokens(
    prompt
)

    print(
    f"[TOKEN ESTIMATE] {token_count}"
)
    generation_start = time.perf_counter()
    answer = generator.generate(
        prompt
    )
    generation_latency = time.perf_counter() - generation_start

    total_latency = time.perf_counter() - overall_start
    print(
    f"[TOTAL QUERY] "
    f"{total_latency:.2f}s"
)

    # Log metrics for observability
    log_query_metrics(
        query=question,
        budget_metrics=budget_result["metrics"],
        latencies={
            "retrieval": retrieval_latency,
            "memory": memory_latency,
            "budget": budget_latency,
            "prompt_build": prompt_build_latency,
            "generation": generation_latency,
            "total": total_latency,
        },
        session_id=session_id,
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
