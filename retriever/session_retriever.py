"""
retriever/session_retriever.py

Implements conversational session context retrieval from the Session
Layer.
"""

from __future__ import annotations

from typing import Callable

from retriever.session_context import SessionContext, SessionMessage


class SessionRetriever:
    """
    Retrieves recent conversational context from the Session Layer.

    Purpose:
        Retrieves the active session summary and recent messages as an
        immutable SessionContext. SessionRetriever owns session retrieval
        only — it never retrieves documents, persistent memory, or
        performs summarization.

    Owned by:
        retriever/session_retriever.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Never retrieves documents.
        - Never retrieves persistent memory.
        - Never performs summarization.
        - Never performs budgeting.
        - Domain layer remains independent from infrastructure; the
          actual session accessor functions are injected at
          construction.
    """

    def __init__(
        self,
        get_summary_fn: Callable[[str], str],
        get_messages_fn: Callable[[str], list[SessionMessage]],
    ) -> None:
        """
        Initialise SessionRetriever with infrastructure accessor
        functions.

        Parameters:
            get_summary_fn (Callable[[str], str]):
                A function that accepts a session_id and returns the
                session summary string. Returns an empty string if no
                summary exists.

            get_messages_fn (Callable[[str], list[SessionMessage]]):
                A function that accepts a session_id and returns a list
                of recent SessionMessages. Returns an empty list if no
                messages exist.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._get_summary_fn = get_summary_fn
        self._get_messages_fn = get_messages_fn

    def retrieve(self, session_id: str) -> SessionContext:
        """
        Retrieve conversational session context for the given session.

        Parameters:
            session_id (str): The identifier of the active session.

        Returns:
            SessionContext: Immutable context containing the session
            summary, recent messages, and metadata.

        Raises:
            None. Empty retrieval is valid and returns a SessionContext
            with an empty summary and no messages.

        Side Effects:
            None. The accessor functions may access infrastructure, but
            SessionRetriever itself performs no side effects.
        """
        summary = self._get_summary_fn(session_id)
        messages = self._get_messages_fn(session_id)
        return SessionContext(
            summary=summary,
            recent_messages=tuple(messages),
            metadata={
                "session_id": session_id,
                "message_count": len(messages),
            },
        )
