SUMMARY_THRESHOLD = 100
RECENT_KEEP = 5

_sessions = {}


def append_message(
    session_id: str,
    role: str,
    content: str
):

    if session_id not in _sessions:
        _sessions[session_id] = []

    _sessions[session_id].append(
        {
            "role": role,
            "content": content
        }
    )


def get_recent_messages(
    session_id: str
):

    return _sessions.get(
        session_id,
        []
    )


def clear_recent_messages(
    session_id: str
):

    _sessions[session_id] = []

def estimated_chars(
    session_id: str
) -> int:

    messages = get_recent_messages(
        session_id
    )

    return sum(
        len(
            msg["content"]
        )
        for msg in messages
    )
CHAR_THRESHOLD = 8000

def should_summarize(
    session_id: str
) -> bool:

    messages = get_recent_messages(
        session_id
    )

    return (
        len(messages)
        >= SUMMARY_THRESHOLD
        or
        estimated_chars(
            session_id
        )
        >= CHAR_THRESHOLD
    )

    


def pop_messages_for_summary(
    session_id: str,
    keep_last: int = RECENT_KEEP
) -> list:

    messages = get_recent_messages(
        session_id
    )

    if len(messages) <= keep_last:
        to_summarize = list(
            messages
        )
        _sessions[session_id] = []
    else:
        split_at = (
            len(messages)
            - keep_last
        )
        to_summarize = messages[
            :split_at
        ]
        _sessions[session_id] = messages[
            split_at:
        ]

    return to_summarize