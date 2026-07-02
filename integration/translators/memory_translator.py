"""
integration/translators/memory_translator.py

Translates between Memory infrastructure objects and Domain objects.
"""

from __future__ import annotations

from retriever.memory_context import MemoryEntry


class MemoryTranslator:
    """
    Translates between Memory infrastructure objects and Domain
    objects.

    Purpose:
        Converts raw infrastructure memory search results (from the
        MemoryGateway) into immutable MemoryEntry domain objects.
        Translation is deterministic and lossless where possible.

    Owned by:
        integration/translators/memory_translator.py

    Consumed by:
        MemoryIntegration.

    Invariants:
        - Never accesses infrastructure.
        - Never coordinates workflows.
        - Never performs business logic.
        - Translation is deterministic: the same infrastructure
          response always produces the same list of MemoryEntry.
    """

    def to_domain(self, results: dict[str, list]) -> list[MemoryEntry]:
        """
        Convert raw infrastructure memory results into a list of
        Domain MemoryEntry objects.

        Parameters:
            results (dict[str, list]): Raw infrastructure response
                containing "ids", "documents", and "distances" keys.

        Returns:
            list[MemoryEntry]: Immutable domain memory entries.

        Raises:
            None. Invalid or missing fields are handled defensively
            by returning empty entries for missing data.

        Side Effects:
            None.
        """
        entries: list[MemoryEntry] = []

        documents = results.get("documents", [])
        ids = results.get("ids", [])
        distances = results.get("distances", [])

        for idx, content in enumerate(documents):
            if not isinstance(content, str):
                continue

            memory_id = ids[idx] if idx < len(ids) else None
            memory_id = memory_id if isinstance(memory_id, str) else None

            distance = distances[idx] if idx < len(distances) else None
            score: float | None = None
            if isinstance(distance, (int, float)):
                score = float(distance)

            entries.append(
                MemoryEntry(
                    content=content,
                    memory_id=memory_id,
                    score=score,
                )
            )

        return entries
