"""
retriever/retrieval_validator.py

Stateless validation of a candidate RetrievedContext, applied by
RetrievalBuilder before a RetrievedContext is returned to callers.
"""

from __future__ import annotations

from retriever.exceptions import RetrievalValidationError, UnsupportedSchemaVersionError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import CURRENT_SCHEMA_VERSION, RetrievedContext
from retriever.session_context import SessionContext, SessionMessage

_KNOWN_SCHEMA_VERSIONS = frozenset({CURRENT_SCHEMA_VERSION})


class RetrievalValidator:
    """
    Validates a candidate RetrievedContext before it is returned by
    RetrievalBuilder.

    Purpose:
        Performs structural, logical, semantic, and version validation
        of a candidate RetrievedContext and reports every violation
        found in a single, precise error. It never repairs, infers, or
        mutates the context it inspects.

    Owned by:
        retriever/retrieval_validator.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Performs no retrieval, no infrastructure access, no
          configuration or environment access.
        - Never mutates the RetrievedContext or any of its fields.
        - Validation is deterministic and side-effect-free: the same
          RetrievedContext always produces the same validation result.
        - Validation is exhaustive: all violations across all
          categories are reported together, not just the first one
          encountered.
    """

    @staticmethod
    def validate(retrieved_context: RetrievedContext) -> None:
        """
        Validate a candidate RetrievedContext.

        Parameters:
            retrieved_context (RetrievedContext): The candidate context
                to validate. Not mutated.

        Returns:
            None. Absence of an exception means the context is valid.

        Raises:
            RetrievalValidationError: If one or more structural,
                logical, or semantic violations are found. The message
                lists every violation found, not just the first.
            UnsupportedSchemaVersionError: If the schema version is not
                recognized.

        Side Effects:
            None.
        """
        violations: list[str] = []
        violations.extend(_validate_structural(retrieved_context))
        violations.extend(_validate_logical(retrieved_context))
        violations.extend(_validate_semantic(retrieved_context))
        violations.extend(_validate_version(retrieved_context))

        if violations:
            raise RetrievalValidationError(
                "RetrievedContext failed validation:\n- "
                + "\n- ".join(violations)
            )


def _validate_structural(context: RetrievedContext) -> list[str]:
    """Check that every field has the type the architecture declares."""
    violations: list[str] = []

    if not isinstance(context, RetrievedContext):
        return [
            f"root: expected RetrievedContext, got "
            f"{type(context).__name__}"
        ]

    if not isinstance(context.knowledge, KnowledgeContext):
        violations.append(
            f"knowledge: expected KnowledgeContext, got "
            f"{type(context.knowledge).__name__}"
        )
    else:
        for idx, item in enumerate(context.knowledge.items):
            if not isinstance(item, KnowledgeItem):
                violations.append(
                    f"knowledge.items[{idx}]: expected KnowledgeItem, "
                    f"got {type(item).__name__}"
                )

    if not isinstance(context.memory, MemoryContext):
        violations.append(
            f"memory: expected MemoryContext, got "
            f"{type(context.memory).__name__}"
        )
    else:
        for idx, entry in enumerate(context.memory.entries):
            if not isinstance(entry, MemoryEntry):
                violations.append(
                    f"memory.entries[{idx}]: expected MemoryEntry, "
                    f"got {type(entry).__name__}"
                )

    if not isinstance(context.session, SessionContext):
        violations.append(
            f"session: expected SessionContext, got "
            f"{type(context.session).__name__}"
        )
    else:
        for idx, msg in enumerate(context.session.recent_messages):
            if not isinstance(msg, SessionMessage):
                violations.append(
                    f"session.recent_messages[{idx}]: expected "
                    f"SessionMessage, got {type(msg).__name__}"
                )

    if not isinstance(context.metadata, RetrievalMetadata):
        violations.append(
            f"metadata: expected RetrievalMetadata, got "
            f"{type(context.metadata).__name__}"
        )

    if not isinstance(context.version, int):
        violations.append(
            f"version: expected int, got {type(context.version).__name__}"
        )

    return violations


def _validate_logical(context: RetrievedContext) -> list[str]:
    """Check that each field's value is internally consistent."""
    if not isinstance(context, RetrievedContext):
        return []

    violations: list[str] = []

    if isinstance(context.version, int) and context.version < 1:
        violations.append(f"version: must be >= 1, got {context.version}")

    if isinstance(context.metadata, RetrievalMetadata):
        if context.metadata.knowledge_count < 0:
            violations.append(
                f"metadata.knowledge_count: must be >= 0, got "
                f"{context.metadata.knowledge_count}"
            )

        if context.metadata.memory_count < 0:
            violations.append(
                f"metadata.memory_count: must be >= 0, got "
                f"{context.metadata.memory_count}"
            )

        if context.metadata.session_count < 0:
            violations.append(
                f"metadata.session_count: must be >= 0, got "
                f"{context.metadata.session_count}"
            )

        if context.metadata.knowledge_latency_ms < 0:
            violations.append(
                f"metadata.knowledge_latency_ms: must be >= 0, got "
                f"{context.metadata.knowledge_latency_ms}"
            )

        if context.metadata.memory_latency_ms < 0:
            violations.append(
                f"metadata.memory_latency_ms: must be >= 0, got "
                f"{context.metadata.memory_latency_ms}"
            )

        if context.metadata.session_latency_ms < 0:
            violations.append(
                f"metadata.session_latency_ms: must be >= 0, got "
                f"{context.metadata.session_latency_ms}"
            )

        if context.metadata.total_latency_ms < 0:
            violations.append(
                f"metadata.total_latency_ms: must be >= 0, got "
                f"{context.metadata.total_latency_ms}"
            )

        if context.metadata.schema_version < 1:
            violations.append(
                f"metadata.schema_version: must be >= 1, got "
                f"{context.metadata.schema_version}"
            )

        # Count consistency: metadata counts must match actual counts
        if isinstance(context.knowledge, KnowledgeContext):
            actual = len(context.knowledge.items)
            if context.metadata.knowledge_count != actual:
                violations.append(
                    f"metadata.knowledge_count ({context.metadata.knowledge_count}) "
                    f"does not match actual knowledge item count ({actual})"
                )

        if isinstance(context.memory, MemoryContext):
            actual = len(context.memory.entries)
            if context.metadata.memory_count != actual:
                violations.append(
                    f"metadata.memory_count ({context.metadata.memory_count}) "
                    f"does not match actual memory entry count ({actual})"
                )

        if isinstance(context.session, SessionContext):
            actual = len(context.session.recent_messages)
            if context.metadata.session_count != actual:
                violations.append(
                    f"metadata.session_count ({context.metadata.session_count}) "
                    f"does not match actual session message count ({actual})"
                )

    return violations


def _validate_semantic(context: RetrievedContext) -> list[str]:
    """Check that meaning matches architecture."""
    if not isinstance(context, RetrievedContext):
        return []

    violations: list[str] = []

    # Semantic ownership: each context must contain only its own type
    if isinstance(context.knowledge, KnowledgeContext):
        for idx, item in enumerate(context.knowledge.items):
            if not isinstance(item, KnowledgeItem):
                violations.append(
                    f"knowledge.items[{idx}]: semantic violation — "
                    f"KnowledgeContext contains non-KnowledgeItem"
                )

    if isinstance(context.memory, MemoryContext):
        for idx, entry in enumerate(context.memory.entries):
            if not isinstance(entry, MemoryEntry):
                violations.append(
                    f"memory.entries[{idx}]: semantic violation — "
                    f"MemoryContext contains non-MemoryEntry"
                )

    if isinstance(context.session, SessionContext):
        for idx, msg in enumerate(context.session.recent_messages):
            if not isinstance(msg, SessionMessage):
                violations.append(
                    f"session.recent_messages[{idx}]: semantic violation — "
                    f"SessionContext contains non-SessionMessage"
                )

    return violations


def _validate_version(context: RetrievedContext) -> list[str]:
    """Check schema version compatibility."""
    if not isinstance(context, RetrievedContext):
        return []

    violations: list[str] = []

    if (
        isinstance(context.version, int)
        and context.version not in _KNOWN_SCHEMA_VERSIONS
    ):
        violations.append(
            f"version: {context.version} has no known semantic meaning to this "
            f"validator (known versions: {sorted(_KNOWN_SCHEMA_VERSIONS)})"
        )

    return violations
