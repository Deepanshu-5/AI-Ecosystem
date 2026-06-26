import time
import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from llm.ollama_generator import (
    OllamaGenerator
)
from conversation_memory.metrics import (
    summary_metrics
)
from config.settings import SUMMARY_MODEL

def _format_messages(
    messages: list[dict]
) -> str:

    lines = []

    for message in messages:
        role = message.get(
            "role",
            "user"
        )
        content = message.get(
            "content",
            ""
        )
        lines.append(
            f"{role}: {content}"
        )

    return "\n".join(
        lines
    )


def summarize_session(
    existing_summary: str,
    messages: list[dict]
) -> str:

    if not messages:
        return existing_summary

    if not existing_summary.strip():
        return _summarize_messages(
            messages
        )

    return _merge_summary(
        existing_summary,
        messages
    )


def _summarize_messages(
    messages: list[dict]
) -> str:

    generator = OllamaGenerator(SUMMARY_MODEL)
    chat_text = _format_messages(
        messages
    )

    prompt = f"""
You are a conversation compression system.

Summarize this session for future context.

Rules:

1. Keep topics discussed, decisions made, and open questions.
2. Keep the current task or goal of the session.
3. Remove greetings, filler, and repetition.
4. Do not extract long-term user facts — only session context.
5. Produce ONE paragraph only.
6. Maximum 150 words.
7. Output only the summary.

Conversation:

{chat_text}

Summary:
"""

    start = time.perf_counter()

    summary = generator.generate(
    prompt
)

    elapsed = (
    time.perf_counter()
    - start
)
    summary_metrics[
    "summaries_created"
] += 1

    summary_metrics[
    "summary_seconds"
].append(elapsed)


    return summary


def _merge_summary(
    existing_summary: str,
    messages: list[dict]
) -> str:

    generator = OllamaGenerator(SUMMARY_MODEL)
    chat_text = _format_messages(
        messages
    )

    prompt = f"""
You are a conversation compression system.

Update the existing session summary with new messages.

Rules:

1. Merge the existing summary with new information.
2. Keep topics discussed, decisions made, and open questions.
3. Keep the current task or goal of the session.
4. Remove outdated or superseded details.
5. Remove greetings, filler, and repetition.
6. Do not extract long-term user facts — only session context.
7. Produce ONE paragraph only.
8. Maximum 150 words.
9. Output only the updated summary.

Existing summary:

{existing_summary}

New messages:

{chat_text}

Updated summary:
"""
    start = time.perf_counter()

    summary = generator.generate(
    prompt
)

    elapsed = (
    time.perf_counter()
    - start
)
    summary_metrics[
    "summaries_created"
] += 1

    summary_metrics[
    "summary_seconds"
].append(
    elapsed
)


    return summary
    


