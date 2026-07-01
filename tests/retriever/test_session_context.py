"""
tests/retriever/test_session_context.py

Unit tests for SessionMessage and SessionContext.
"""

import pytest

from retriever.session_context import SessionContext, SessionMessage


class TestSessionMessage:
    def test_creation(self) -> None:
        msg = SessionMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_immutability(self) -> None:
        msg = SessionMessage(role="user", content="Hello")
        with pytest.raises(AttributeError):
            msg.role = "assistant"  # type: ignore[misc]

    def test_to_dict(self) -> None:
        msg = SessionMessage(role="user", content="Hello")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Hello"}


class TestSessionContext:
    def test_creation(self) -> None:
        msg = SessionMessage(role="user", content="Hello")
        ctx = SessionContext(
            summary="Previous discussion",
            recent_messages=(msg,),
            metadata={"key": "value"},
        )
        assert ctx.summary == "Previous discussion"
        assert len(ctx.recent_messages) == 1
        assert ctx.metadata == {"key": "value"}

    def test_empty_context(self) -> None:
        ctx = SessionContext(
            summary="",
            recent_messages=(),
            metadata={},
        )
        assert ctx.summary == ""
        assert len(ctx.recent_messages) == 0

    def test_immutability(self) -> None:
        ctx = SessionContext(summary="", recent_messages=(), metadata={})
        with pytest.raises(AttributeError):
            ctx.summary = "Modified"  # type: ignore[misc]

    def test_to_dict(self) -> None:
        msg = SessionMessage(role="user", content="Hello")
        ctx = SessionContext(
            summary="Previous discussion",
            recent_messages=(msg,),
            metadata={"count": 1},
        )
        d = ctx.to_dict()
        assert d["summary"] == "Previous discussion"
        assert d["recent_messages"] == [{"role": "user", "content": "Hello"}]
        assert d["metadata"] == {"count": 1}
