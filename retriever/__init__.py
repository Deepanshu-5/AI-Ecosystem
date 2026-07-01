"""
retriever/__init__.py

Public API of the Retrieval subsystem.

Only stable, downstream-facing contracts are re-exported here.
Internal modules (retrieval_builder, retrieval_validator, individual
retrievers) are importable directly but are not re-exported to keep
the public surface minimal.
"""

from retriever.exceptions import (
    InvalidExecutionPlanError,
    RetrievalValidationError,
    RetrieverError,
    UnsupportedSchemaVersionError,
)
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext, SessionMessage

__all__ = [
    # Exceptions
    "RetrieverError",
    "RetrievalValidationError",
    "InvalidExecutionPlanError",
    "UnsupportedSchemaVersionError",
    # Domain objects
    "RetrievedContext",
    "KnowledgeContext",
    "KnowledgeItem",
    "MemoryContext",
    "MemoryEntry",
    "SessionContext",
    "SessionMessage",
    "RetrievalMetadata",
]
