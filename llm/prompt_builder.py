def _section(
    title: str,
    content: str
) -> str:

    if not content.strip():
        return ""

    return f"""
====================
{title}
====================

{content}
"""


def build_prompt(
    question: str,
    knowledge_context: str,
    memory_context: str = "",
    conversation_summary: str = "",
    recent_messages: str = ""
):

    conversation_block = _section(
        "CONVERSATION SUMMARY",
        conversation_summary
    )

    recent_block = _section(
        "RECENT MESSAGES",
        recent_messages
    )

    memory_block = _section(
        "RELEVANT MEMORIES",
        memory_context
    )

    knowledge_block = _section(
        "RELEVANT KNOWLEDGE",
        knowledge_context
    )

    return f"""
You are a retrieval assistant.

Use the provided information to answer.

If the information is insufficient, say so.
{conversation_block}{recent_block}{memory_block}{knowledge_block}
====================
QUESTION
====================

{question}
Rules:

- Answer in one sentence.
- Maximum 20 words.
- Do not explain your reasoning.
- Do not show analysis.

ANSWER:
"""