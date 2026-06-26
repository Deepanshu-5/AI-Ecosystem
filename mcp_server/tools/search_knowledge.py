from services.context_budgeter import get_budgeter
from services.knowledge_service import search
from services.context_service import build_context
from memory.memory_service import recall
from conversation_memory.session_memory import (
    get_session_context,
)


def _section(
    title: str,
    content: str
) -> str:

    if not content.strip():
        return ""

    return f"=== {title} ===\n{content}"


# mcp_server/tools/search_knowledge.py
def search_knowledge(question: str, session_id: str = "") -> str:
    # Gather raw components
    conversation_summary = ""
    recent_messages = ""
    if session_id:
        session = get_session_context(session_id)
        conversation_summary = session["summary"]
        recent_messages = session["recent_messages"]

    memories = recall(question)
    memory_context = "\n".join(memories) if memories else ""

    chunks = search(question)
    knowledge_context = build_context(chunks)

    # Apply context budgeting before returning to Claude
    budgeter = get_budgeter()
    budget_result = budgeter.build_context(
        question=question,
        knowledge_context=knowledge_context,
        memory_context=memory_context,
        conversation_summary=conversation_summary,
        recent_messages=recent_messages,
    )

    parts = []
    summary_block = _section(
        "CONVERSATION SUMMARY",
        budget_result["conversation_summary"],
    )
    if summary_block:
        parts.append(summary_block)

    recent_block = _section(
        "RECENT MESSAGES",
        budget_result["recent_messages"],
    )
    if recent_block:
        parts.append(recent_block)

    memory_block = _section(
        "RELEVANT MEMORIES",
        budget_result["memory_context"],
    )
    if memory_block:
        parts.append(memory_block)

    knowledge_block = _section(
        "RELEVANT KNOWLEDGE",
        budget_result["knowledge_context"],
    )
    if knowledge_block:
        parts.append(knowledge_block)

    if not parts:
        return "No relevant context found."

    return "\n\n".join(parts)
    # REMOVED: process_message(session_id, "user", question)
