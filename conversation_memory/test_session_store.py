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
    should_summarize
)

for i in range(20):
    append_message(
        "test_session",
        "user",
        f"message {i}"
    )

print(
    len(
        get_recent_messages(
            "test_session"
        )
    )
)

print(
    should_summarize(
        "test_session"
    )
)