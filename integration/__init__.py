"""
integration/__init__.py

Public API of the Integration Layer.

Only the RetrieverIntegration entry point and Integration exceptions
are re-exported. Internal components (Gateways, Translators,
individual Integrations) are importable directly but are not
re-exported to keep the public surface minimal.
"""

from integration.exceptions import (
    IntegrationError,
    KnowledgeIntegrationError,
    MemoryIntegrationError,
    SessionIntegrationError,
)
from integration.integrations.retriever_integration import RetrieverIntegration

__all__ = [
    "RetrieverIntegration",
    "IntegrationError",
    "KnowledgeIntegrationError",
    "MemoryIntegrationError",
    "SessionIntegrationError",
]
