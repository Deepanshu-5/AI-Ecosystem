"""
integration/translators/session_translator.py

Translates between Session infrastructure objects and Domain objects.
"""

from __future__ import annotations

from retriever.session_context import SessionMessage


class SessionTranslator:
    """
    Translates between Session infrastructure objects and Domain
    objects.

    Purpose:
        Converts raw infrastructure session message dictionaries (from
        the SessionGateway) into immutable SessionMessage domain
        objects. Translation is deterministic and lossless.

    Owned by:
        integration/translators/session_translator.py

    Consumed by:
        SessionIntegration.

    Invariants:
        - Never accesses infrastructure.
        - Never coordinates workflows.
        - Never performs business logic.
        - Translation is deterministic: the same message dictionary
          always produces the same SessionMessage.
    """

    def to_domain(self, msg: dict[str, str]) -> SessionMessage:
        """
        Convert an infrastructure message dictionary into a Domain
        SessionMessage.

        Parameters:
            msg (dict[str, str]): Raw infrastructure message with
                "role" and "content" keys.

        Returns:
            SessionMessage: Immutable domain session message.

        Raises:
            None. Invalid or missing fields are handled defensively
            by using empty strings as defaults.

        Side Effects:
            None.
        """
        role = msg.get("role", "")
        content = msg.get("content", "")

        return SessionMessage(
            role=role,
            content=content,
        )
