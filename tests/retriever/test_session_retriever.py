"""
tests/retriever/test_session_retriever.py

Component tests for SessionRetriever.
"""

import pytest

from retriever.session_context import SessionContext, SessionMessage
from retriever.session_retriever import SessionRetriever


class TestSessionRetriever:
    def _make_retriever(
        self,
        summary: str = "",
        messages: list[SessionMessage] | None = None,
    ) -> SessionRetriever:
        def get_summary_fn(session_id: str) -> str:
            return summary

        def get_messages_fn(session_id: str) -> list[SessionMessage]:
            return list(messages) if messages is not None else []

        return SessionRetriever(
            get_summary_fn=get_summary_fn,
            get_messages_fn=get_messages_fn,
        )

    def test_retrieve_with_summary_and_messages(self) -> None:
        messages = [
            SessionMessage(role="user", content="Hello"),
            SessionMessage(role="assistant", content="Hi there"),
        ]
        retriever = self._make_retriever(
            summary="Previous discussion about Python",
            messages=messages,
        )
        ctx = retriever.retrieve("session_123")

        assert isinstance(ctx, SessionContext)
        assert ctx.summary == "Previous discussion about Python"
        assert len(ctx.recent_messages) == 2
        assert ctx.recent_messages[0].role == "user"
        assert ctx.metadata["session_id"] == "session_123"
        assert ctx.metadata["message_count"] == 2

    def test_retrieve_empty(self) -> None:
        retriever = self._make_retriever()
        ctx = retriever.retrieve("session_123")

        assert isinstance(ctx, SessionContext)
        assert ctx.summary == ""
        assert len(ctx.recent_messages) == 0
        assert ctx.metadata["message_count"] == 0

    def test_retrieve_deterministic(self) -> None:
        messages = [SessionMessage(role="user", content="Hello")]
        retriever = self._make_retriever(
            summary="Summary",
            messages=messages,
        )
        ctx1 = retriever.retrieve("session_123")
        ctx2 = retriever.retrieve("session_123")
        assert ctx1 == ctx2

    def test_accessor_receives_session_id(self) -> None:
        received_ids: list[str] = []

        def get_summary_fn(session_id: str) -> str:
            received_ids.append(session_id)
            return ""

        def get_messages_fn(session_id: str) -> list[SessionMessage]:
            return []

        retriever = SessionRetriever(
            get_summary_fn=get_summary_fn,
            get_messages_fn=get_messages_fn,
        )
        retriever.retrieve("session_456")
        assert received_ids == ["session_456"]
