"""
integration/integrations/session_integration.py

Coordinates session retrieval through the Integration Layer.
"""

from __future__ import annotations

from integration.gateways.session_gateway import SessionGateway
from integration.translators.session_translator import SessionTranslator
from retriever.session_context import SessionMessage


class SessionIntegration:
    """
    Coordinates session retrieval through the Integration Layer.

    Purpose:
        Orchestrates the session retrieval workflow: invokes the
        SessionGateway to access infrastructure, then invokes the
        SessionTranslator to convert infrastructure responses into
        Domain SessionMessages. Returns the Domain objects upstream.

    Owned by:
        integration/integrations/session_integration.py

    Consumed by:
        RetrieverIntegration.

    Invariants:
        - Never accesses infrastructure directly.
        - Never performs translation itself.
        - Never coordinates knowledge or memory retrieval.
        - Owns session workflow only.
    """

    def __init__(
        self,
        gateway: SessionGateway | None = None,
        translator: SessionTranslator | None = None,
    ) -> None:
        """
        Initialise SessionIntegration.

        Parameters:
            gateway (SessionGateway | None): Gateway for
                infrastructure communication. If None, a default
                SessionGateway is constructed.
            translator (SessionTranslator | None): Translator for
                object conversion. If None, a default
                SessionTranslator is constructed.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._gateway = gateway if gateway is not None else SessionGateway()
        self._translator = translator if translator is not None else SessionTranslator()

    def get_summary(self, session_id: str) -> str:
        """
        Retrieve a session summary through the Integration Layer.

        Parameters:
            session_id (str): The session identifier.

        Returns:
            str: The session summary. Returns an empty string if no
            summary exists.

        Raises:
            SessionIntegrationError: Propagated from the Gateway if an
                infrastructure failure occurs.

        Side Effects:
            None.
        """
        return self._gateway.load_summary(session_id)

    def get_messages(self, session_id: str) -> list[SessionMessage]:
        """
        Retrieve recent session messages through the Integration
        Layer.

        Parameters:
            session_id (str): The session identifier.

        Returns:
            list[SessionMessage]: Immutable domain session messages.

        Raises:
            SessionIntegrationError: Propagated from the Gateway or
                Translator if an infrastructure failure occurs.

        Side Effects:
            None.
        """
        raw_messages = self._gateway.get_recent_messages(session_id)
        return [self._translator.to_domain(msg) for msg in raw_messages]
