"""
retriever/session_context.py

Domain object representing conversational session context retrieved
from the Session Layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionMessage:
    """
    A single message within a conversational session.

    Purpose:
        Represents one message (user or assistant) retrieved from the
        Session Layer for conversational continuity.

    Owned by:
        retriever/session_context.py

    Consumed by:
        SessionContext, SessionRetriever, RetrievalBuilder.

    Invariants:
        - role is a non-empty string (e.g., "user", "assistant").
        - content is a non-empty string representing the message text.
    """

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, str]: Mapping with fixed key order: role,
            content.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass(frozen=True)
class SessionContext:
    """
    Represents the conversational session context retrieved for a
    single query.

    Purpose:
        Aggregates a session summary and recent messages into a single
        immutable context object for downstream consumption by the
        Context Budgeter.

    Owned by:
        retriever/session_context.py

    Consumed by:
        RetrievedContext, RetrievalBuilder, RetrievalValidator.

    Invariants:
        - Contains only session-related information; no long-term
          memory, no knowledge items, no documents.
        - recent_messages is an immutable tuple; never a mutable list.
        - summary is optional and may be empty if no summary exists.
        - metadata is informational only and never influences
          retrieval behavior.
    """

    summary: str
    recent_messages: tuple[SessionMessage, ...]
    metadata: dict[str, object]
    @classmethod
    def empty(cls) -> "SessionContext":
        return cls(
            summary="",
            recent_messages=(),
            metadata={},
        )
    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: summary,
            recent_messages, metadata. Messages are serialized
            recursively.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "summary": self.summary,
            "recent_messages": [
                msg.to_dict() for msg in self.recent_messages
            ],
            "metadata": dict(self.metadata),
        }
