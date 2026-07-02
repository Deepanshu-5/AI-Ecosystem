"""
integration/gateways/session_gateway.py

Adapts existing Conversation Memory infrastructure for the
Integration Layer.
"""

from __future__ import annotations

from typing import Callable

from integration.exceptions import SessionIntegrationError


class SessionGateway:
    """
    Adapts existing Conversation Memory infrastructure.

    Purpose:
        Provides controlled access to the existing Session Storage
        (conversation_memory.session_store and
        conversation_memory.session_manager). The Gateway calls the
        infrastructure, handles infrastructure-level exceptions, and
        returns raw infrastructure responses. No translation occurs
        here.

    Owned by:
        integration/gateways/session_gateway.py

    Consumed by:
        SessionIntegration.

    Invariants:
        - Never performs translation.
        - Never constructs Domain objects.
        - Never performs business logic.
        - Infrastructure exceptions are caught and translated into
          SessionIntegrationError.
    """

    def __init__(
        self,
        load_summary_fn: Callable[[str], str] = None,
        get_messages_fn: Callable[[str], list[dict[str, str]]] = None,
    ) -> None:
        """
        Initialise SessionGateway.

        Parameters:
            load_summary_fn: Optional function to load a session
                summary. If None, the default
                conversation_memory.session_store.load_summary is used.
            get_messages_fn: Optional function to retrieve recent
                messages. If None, the default
                conversation_memory.session_manager.get_recent_messages
                is used.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        if load_summary_fn is None:
            from conversation_memory.session_store import load_summary as _default_load

            self._load_summary_fn = _default_load
        else:
            self._load_summary_fn = load_summary_fn

        if get_messages_fn is None:
            from conversation_memory.session_manager import (
                get_recent_messages as _default_messages,
            )

            self._get_messages_fn = _default_messages
        else:
            self._get_messages_fn = get_messages_fn

    def load_summary(self, session_id: str) -> str:
        """
        Retrieve a session summary from the existing infrastructure.

        Parameters:
            session_id (str): The session identifier.

        Returns:
            str: The session summary. Returns an empty string if no
            summary exists.

        Raises:
            SessionIntegrationError: If the infrastructure access fails.

        Side Effects:
            None.
        """
        try:
            return self._load_summary_fn(session_id)
        except Exception as exc:
            raise SessionIntegrationError(
                f"Session summary load failed for session_id: {session_id!r}"
            ) from exc

    def get_recent_messages(self, session_id: str) -> list[dict[str, str]]:
        """
        Retrieve recent messages from the existing infrastructure.

        Parameters:
            session_id (str): The session identifier.

        Returns:
            list[dict[str, str]]: Raw message dictionaries, each
            containing "role" and "content" keys.

        Raises:
            SessionIntegrationError: If the infrastructure access fails.

        Side Effects:
            None.
        """
        try:
            return self._get_messages_fn(session_id)
        except Exception as exc:
            raise SessionIntegrationError(
                f"Session message retrieval failed for session_id: {session_id!r}"
            ) from exc
