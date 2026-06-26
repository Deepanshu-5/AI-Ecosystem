from pathlib import Path
import json


from pathlib import Path

ROOT = Path(
    __file__
).resolve().parent.parent

CONVERSATION_DIR = (
    ROOT
    / "data"
    / "conversations"
)

CONVERSATION_DIR.mkdir(
    parents=True,
    exist_ok=True
)




def _get_session_path(
    session_id: str
) -> Path:
    return CONVERSATION_DIR / f"{session_id}.json"


def save_summary(
    session_id: str,
    summary: str
) -> None:

    session_file = _get_session_path(
        session_id
    )

    data = {
        "session_id": session_id,
        "summary": summary
    }

    with open(
        session_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def load_summary(
    session_id: str
) -> str:

    session_file = _get_session_path(
        session_id
    )

    if not session_file.exists():
        return ""

    with open(
        session_file,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    return data.get(
        "summary",
        ""
    )


def session_exists(
    session_id: str
) -> bool:

    session_file = _get_session_path(
        session_id
    )

    return session_file.exists()
if __name__ == "__main__":
    save_summary(
    "test_session",
    "This is a test summary."
)

    print(
    load_summary(
        "test_session"
    )
)

    print(
    session_exists(
        "test_session"
    )
)