def build_prompt(
    question: str,
    knowledge_context: str,
    memory_context: str = "",
    conversation_summary: str = "",
    recent_messages: str = ""
):

    return f"""
You are a retrieval assistant.

Use the provided information to answer.

If the information is insufficient, say so.

====================
CONVERSATION SUMMARY
====================

{conversation_summary}

====================
RECENT MESSAGES
====================

{recent_messages}

====================
RELEVANT MEMORIES
====================

{memory_context}

====================
RELEVANT KNOWLEDGE
====================

{knowledge_context}

====================
QUESTION
====================

{question}

ANSWER:
"""