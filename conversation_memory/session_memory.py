import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from conversation_memory.session_manager import (
    append_message,
    get_recent_messages,
    should_summarize,
    pop_messages_for_summary,
    RECENT_KEEP
)

from conversation_memory.session_store import (
    load_summary,
    save_summary
)

from conversation_memory.session_summarizer import (
    summarize_session
)
from conversation_memory.metrics import (summary_metrics)


def format_recent_messages(
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


def process_message(
    session_id: str,
    role: str,
    content: str
) -> None:
  
    append_message(
        session_id,
        role,
        content
    )
    summary_metrics[
    "messages_processed"
] += 1

    if not should_summarize(session_id):
         return

    existing = load_summary(
        session_id
    )

    to_summarize = pop_messages_for_summary(
        session_id,
        keep_last=RECENT_KEEP
    )

    new_summary = summarize_session(
        existing,
        to_summarize
    )

    save_summary(
        session_id,
        new_summary
    )


def get_session_context(
    session_id: str
) -> dict:

    summary = load_summary(
        session_id
    )

    recent = get_recent_messages(
        session_id
    )

    return {
        "summary": summary,
        "recent_messages": format_recent_messages(
            recent
        )
    }


def get_metrics():

    summaries = summary_metrics[
        "summary_seconds"
    ]

    avg_time = (
        sum(summaries) / len(summaries)
        if summaries
        else 0
    )

    return {
        "messages_processed":
            summary_metrics[
                "messages_processed"
            ],

        "summaries_created":
            summary_metrics[
                "summaries_created"
            ],

        "avg_summary_seconds":
            round(avg_time, 2)
    }
    
if __name__ == "__main__":

    session_id = "test_orchestrator"

    for i in range(
        105
    ):
        process_message(
            session_id,
            "user",
            f"message {i}"
        )

    context = get_session_context(
        session_id
    )

    print(
        "\nSUMMARY:\n"
    )

    print(
        context["summary"]
    )

    print(
        "\nRECENT MESSAGES:\n"
    )

    print(
        context["recent_messages"]
    )
    print(
    "\nMETRICS:\n"
)

    print(
    get_metrics()
)
