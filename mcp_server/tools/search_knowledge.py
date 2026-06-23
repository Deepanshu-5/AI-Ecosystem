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
    parts = []

    if session_id:
        session = get_session_context(session_id)
        summary_block = _section("CONVERSATION SUMMARY", session["summary"])
        if summary_block:
            parts.append(summary_block)
        recent_block = _section("RECENT MESSAGES", session["recent_messages"])
        if recent_block:
            parts.append(recent_block)

    memories = recall(question)
    if memories:
        parts.append(_section("RELEVANT MEMORIES", "\n".join(memories)))

    chunks = search(question)
    knowledge = build_context(chunks)
    if knowledge.strip():
        parts.append(_section("RELEVANT KNOWLEDGE", knowledge))

    if not parts:
        return "No relevant context found."

    return "\n\n".join(parts)
    # REMOVED: process_message(session_id, "user", question)