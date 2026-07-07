"""
retriever/retrieval_builder.py

Coordinates retrieval operations and assembles the immutable
RetrievedContext.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from planner.execution_plan import ExecutionPlan
from planner.resource_requirements import ResourceRequirements

from retriever.exceptions import InvalidExecutionPlanError
from retriever.knowledge_context import KnowledgeContext
from retriever.knowledge_retriever import KnowledgeRetriever
from retriever.memory_context import MemoryContext
from retriever.memory_retriever import MemoryRetriever
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieval_validator import RetrievalValidator
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext
from retriever.session_retriever import SessionRetriever

if TYPE_CHECKING:
    pass


class RetrievalBuilder:
    """
    Coordinates retrieval operations and assembles a validated,
    immutable RetrievedContext.

    Purpose:
        Consumes an ExecutionPlan, invokes the required individual
        retrievers, collects their outputs, assembles a RetrievedContext,
        validates it, and returns it. The builder performs orchestration
        only — it never performs retrieval logic, validation logic, or
        reads databases directly.

    Owned by:
        retriever/retrieval_builder.py

    Consumed by:
        Control Plane, downstream orchestration layer.

    Invariants:
        - Never performs retrieval logic itself.
        - Never performs validation logic itself.
        - Never reads databases or infrastructure directly.
        - Never builds prompts.
        - Never changes planner decisions.
        - Always validates before returning.
        - Partial construction is not permitted; if any retrieval fails,
          no RetrievedContext is returned.
    """

    def __init__(
        self,
        knowledge_retriever: KnowledgeRetriever | None = None,
        memory_retriever: MemoryRetriever | None = None,
        session_retriever: SessionRetriever | None = None,
    ) -> None:
        """
        Initialise RetrievalBuilder with the required retriever
        instances.

        Parameters:
            knowledge_retriever (KnowledgeRetriever | None):
                The retriever responsible for knowledge retrieval.
                Required when resource_requirements.knowledge is True.

            memory_retriever (MemoryRetriever | None):
                The retriever responsible for memory retrieval.
                Required when resource_requirements.memory is True.

            session_retriever (SessionRetriever | None):
                The retriever responsible for session retrieval.
                Required when resource_requirements.session is True.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._knowledge_retriever = knowledge_retriever
        self._memory_retriever = memory_retriever
        self._session_retriever = session_retriever

    def build(
        self,
        execution_plan: ExecutionPlan,
        query: str,
        session_id: str | None = None,
    ) -> RetrievedContext:
        """
        Orchestrate retrieval and assemble a validated RetrievedContext.

        The builder follows the deterministic retrieval pipeline:
        1. Validate the ExecutionPlan.
        2. Read ResourceRequirements.
        3. Invoke required retrievers in fixed order: Knowledge,
           Memory, Session.
        4. Collect Context objects.
        5. Assemble RetrievedContext.
        6. Validate RetrievedContext.
        7. Return immutable RetrievedContext.

        Parameters:
            execution_plan (ExecutionPlan): The immutable plan produced
                by the Planner. Determines which retrievers are
                invoked.

            query (str): The original user query. Required for knowledge
                and memory retrieval. Must not be empty or whitespace-
                only.

            session_id (str | None): The active session identifier.
                Required when session retrieval is requested. May be
                None if session retrieval is not required.

        Returns:
            RetrievedContext: A validated, immutable context containing
            all retrieved information and metadata.

        Raises:
            InvalidExecutionPlanError: If the execution_plan is None,
                missing required fields, or structurally invalid.
            RetrieverError: If a required retriever is not available
                for a requested resource, or if any retrieval fails.

        Side Effects:
            None. The injected retrievers may access infrastructure,
            but RetrievalBuilder itself performs no side effects.
        """
        start_time = time.perf_counter()

        self._validate_execution_plan(execution_plan)
        self._validate_query(query)

        resource_requirements = execution_plan.resource_requirements

        knowledge_context, knowledge_latency_ms = self._retrieve_knowledge(
         resource_requirements,
          query,
        )
        memory_context, memory_latency_ms = self._retrieve_memory(
         resource_requirements,
          query,
        )
        session_context, session_latency_ms = self._retrieve_session(
            resource_requirements, session_id
        )

        total_latency_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        metadata = RetrievalMetadata(
            knowledge_count=len(knowledge_context.items),
            memory_count=len(memory_context.entries),
            session_count=len(session_context.recent_messages),
            knowledge_latency_ms=knowledge_latency_ms,
            memory_latency_ms=memory_latency_ms,
            session_latency_ms=session_latency_ms,
            total_latency_ms=total_latency_ms,
        )

        retrieved_context = RetrievedContext(
            knowledge=knowledge_context,
            memory=memory_context,
            session=session_context,
            metadata=metadata,
        )

        RetrievalValidator.validate(retrieved_context)
        return retrieved_context

    def _validate_execution_plan(
        self, execution_plan: ExecutionPlan | None
    ) -> None:
        """Validate that the ExecutionPlan is suitable for retrieval."""
        if execution_plan is None:
            raise InvalidExecutionPlanError(
                "execution_plan: must not be None"
            )

        if not isinstance(execution_plan, ExecutionPlan):
            raise InvalidExecutionPlanError(
                f"execution_plan: expected ExecutionPlan, got "
                f"{type(execution_plan).__name__}"
            )

        if not hasattr(execution_plan, "resource_requirements"):
            raise InvalidExecutionPlanError(
                "execution_plan: missing resource_requirements"
            )

        resource_requirements = execution_plan.resource_requirements
        if not isinstance(resource_requirements, ResourceRequirements):
            raise InvalidExecutionPlanError(
                f"execution_plan.resource_requirements: expected "
                f"ResourceRequirements, got "
                f"{type(resource_requirements).__name__}"
            )

    def _validate_query(self, query: str) -> None:
        """Validate that the query is suitable for retrieval."""
        if not isinstance(query, str):
            raise InvalidExecutionPlanError(
                f"query: expected str, got {type(query).__name__}"
            )

        if not query.strip():
            raise InvalidExecutionPlanError(
                "query: must not be empty or whitespace-only"
            )

    def _retrieve_knowledge(
    self,
    resource_requirements: ResourceRequirements,
    query: str,
)-> tuple[KnowledgeContext, int]:
        """
        Retrieve knowledge if requested, or return an empty context.

        Returns:
            tuple[KnowledgeContext, int]: The retrieved context and
            latency in milliseconds.
        """
        if not resource_requirements.knowledge:
            return KnowledgeContext.empty(), 0

        if self._knowledge_retriever is None:
            raise InvalidExecutionPlanError(
                "resource_requirements.knowledge is True but no "
                "KnowledgeRetriever was provided"
            )

        start = time.perf_counter()
        context = self._knowledge_retriever.retrieve(query)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return context, latency_ms

    def _retrieve_memory(
    self,
    resource_requirements: ResourceRequirements,
    query: str,
) -> tuple[MemoryContext, int]:
        """
        Retrieve memory if requested, or return an empty context.

        Returns:
            tuple[MemoryContext, int]: The retrieved context and
            latency in milliseconds.
        """
        if not resource_requirements.memory:
            return MemoryContext.empty(), 0

        if self._memory_retriever is None:
            raise InvalidExecutionPlanError(
                "resource_requirements.memory is True but no "
                "MemoryRetriever was provided"
            )

        start = time.perf_counter()
        context = self._memory_retriever.retrieve(query)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return context, latency_ms

    def _retrieve_session(
        self,
        resource_requirements: ResourceRequirements,
        session_id: str | None,
    ) -> tuple[SessionContext, int]:
        """
        Retrieve session context if requested, or return an empty context.

        Returns:
            tuple[SessionContext, int]: The retrieved context and
            latency in milliseconds.
        """
        if not resource_requirements.session:
            return SessionContext.empty(), 0

        if self._session_retriever is None:
            raise InvalidExecutionPlanError(
                "resource_requirements.session is True but no "
                "SessionRetriever was provided"
            )

        if session_id is None:
            raise InvalidExecutionPlanError(
                "resource_requirements.session is True but no "
                "session_id was provided"
            )

        start = time.perf_counter()
        context = self._session_retriever.retrieve(session_id)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return context, latency_ms
