"""
integration/exceptions.py

Integration Layer exceptions.

Translates infrastructure failures into deterministic domain-level
exceptions. Infrastructure exceptions never cross the Integration
Layer boundary.
"""


class IntegrationError(Exception):
    """
    Base exception for all Integration Layer failures.

    Purpose:
        Provides a single, importable root for every Integration
        Layer exception, preventing infrastructure-level exceptions
        from leaking into Domain subsystems.

    Owned by:
        integration/exceptions.py

    Consumed by:
        All Integration Layer components (Integrations, Gateways,
        Translators) and callers of the Integration Layer.

    Invariants:
        - Carries a human-readable, deterministic message.
        - Never wraps or leaks infrastructure stack traces into the
          Domain Layer.
    """


class KnowledgeIntegrationError(IntegrationError):
    """
    Raised when knowledge retrieval through the Integration Layer
    fails.

    Purpose:
        Signals that the KnowledgeGateway encountered an
        infrastructure failure during knowledge search, or that the
        KnowledgeTranslator received an unexpected infrastructure
        response. The Domain Layer receives this instead of the raw
        infrastructure exception.

    Owned by:
        integration/exceptions.py

    Consumed by:
        KnowledgeIntegration, RetrieverIntegration.

    Invariants:
        - Always carries a message identifying the failure point.
    """


class MemoryIntegrationError(IntegrationError):
    """
    Raised when memory retrieval through the Integration Layer fails.

    Purpose:
        Signals that the MemoryGateway encountered an infrastructure
        failure during memory search, or that the MemoryTranslator
        received an unexpected infrastructure response.

    Owned by:
        integration/exceptions.py

    Consumed by:
        MemoryIntegration, RetrieverIntegration.

    Invariants:
        - Always carries a message identifying the failure point.
    """


class SessionIntegrationError(IntegrationError):
    """
    Raised when session retrieval through the Integration Layer fails.

    Purpose:
        Signals that the SessionGateway encountered an infrastructure
        failure during session access, or that the SessionTranslator
        received an unexpected infrastructure response.

    Owned by:
        integration/exceptions.py

    Consumed by:
        SessionIntegration, RetrieverIntegration.

    Invariants:
        - Always carries a message identifying the failure point.
    """
