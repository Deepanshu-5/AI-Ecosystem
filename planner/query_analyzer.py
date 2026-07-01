"""
planner/query_analyzer.py

Deterministic rule-based analysis of raw user queries into a
PlanningContext for the Planner.
"""

from __future__ import annotations

import re

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.exceptions import PlannerValidationError
from planner.planning_context import PlanningContext
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

_DOCUMENT_KEYWORDS = frozenset({
    "document",
    "pdf",
    "file",
    "attachment",
    "upload",
})

_MEMORY_KEYWORDS = frozenset({
    "remember",
    "memory",
    "know about me",
    "my preference",
})

_SESSION_KEYWORDS = frozenset({
    "earlier",
    "previous",
    "last message",
    "continue",
    "above",
})

_CODE_KEYWORDS = frozenset({
    "code",
    "python",
    "java",
    "cpp",
    "c++",
    "bug",
    "debug",
    "function",
    "class",
    "algorithm",
    "program",
})

_KNOWLEDGE_PREFIXES = (
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "which",
    "explain",
    "define",
)
_HIGH_COMPLEXITY_KEYWORDS = frozenset({
    "design",
    "architecture",
    "plan",
    "roadmap",
    "optimize",
    "optimization",
    "evaluate",
    "analysis",
    "implement",
    "develop",
    "build",
    "system",
    "framework",
})

_MEDIUM_COMPLEXITY_KEYWORDS = frozenset({
    "compare",
    "comparison",
    "difference",
    "summarize",
    "summary",
    "explain",
    "why",
    "review",
    "analyze",
})

class QueryAnalyzer:
    """
    Deterministic analyzer responsible for transforming a raw user query
    into an immutable PlanningContext.

    Purpose:
        Analyze a raw query and determine the Planner's intermediate
        decisions before ExecutionPlan construction.

    Owned by:
        planner/query_analyzer.py

    Consumed by:
        PlannerBuilder (indirectly through PlanningContext).

    Invariants:
        - Stateless.
        - Deterministic.
        - Side-effect free.
        - Performs no retrieval.
        - Performs no routing.
        - Performs no prompt construction.
        - Performs no execution.
        - Performs no infrastructure access.
    """

    @staticmethod
    def analyze(query: str) -> PlanningContext:
        """
        Analyze a raw query and return a PlanningContext.

        Parameters:
            query: Raw user query.

        Returns:
            PlanningContext

        Raises:
            PlannerValidationError:
                If the query is structurally invalid.

        Side Effects:
            None.
        """
        normalized_query = QueryAnalyzer._normalize_query(query)

        processing_goal = QueryAnalyzer._determine_processing_goal(
            normalized_query
        )

        complexity = QueryAnalyzer._estimate_complexity(
            normalized_query
        )

        resource_requirements = (
            QueryAnalyzer._determine_resource_requirements(
                normalized_query,
                processing_goal,
            )
        )

        decision_trace = QueryAnalyzer._build_decision_trace(
            processing_goal,
            complexity,
            resource_requirements,
        )

        return PlanningContext(
            processing_goal=processing_goal,
            complexity=complexity,
            resource_requirements=resource_requirements,
            decision_trace=decision_trace,
        )

    @staticmethod
    def _normalize_query(query: str) -> str:
        """
        Normalize a raw query into a deterministic form suitable for
        rule-based analysis.

        Purpose:
            Remove superficial formatting differences without changing
            the query's semantic meaning.

        Parameters:
            query (str):
                Raw user query.

        Returns:
            str:
                Normalized query.

        Raises:
            PlannerValidationError:
                If the query is not a valid non-empty string.

        Side Effects:
            None.
        """
        if not isinstance(query, str):
            raise PlannerValidationError(
                f"query: expected str, got {type(query).__name__}"
            )

        normalized = query.strip()

        if not normalized:
            raise PlannerValidationError(
                "query: must not be empty or whitespace-only"
            )

        normalized = re.sub(r"\s+", " ", normalized)

        return normalized

    @staticmethod
    def _determine_processing_goal(query: str) -> ProcessingGoal:
        """
    Determine the ProcessingGoal for a normalized query.

    Parameters:
        query (str): Normalized query.

    Returns:
        ProcessingGoal

    Raises:
        None.

    Side Effects:
        None.
        """
        lowered = query.lower()

        if any(keyword in lowered for keyword in _DOCUMENT_KEYWORDS):
         return ProcessingGoal.DOCUMENT

        if any(keyword in lowered for keyword in _MEMORY_KEYWORDS):
         return ProcessingGoal.MEMORY

        if any(keyword in lowered for keyword in _SESSION_KEYWORDS):
          return ProcessingGoal.SESSION

        if any(keyword in lowered for keyword in _CODE_KEYWORDS):
         return ProcessingGoal.CODE

        if lowered.startswith(_KNOWLEDGE_PREFIXES):
          return ProcessingGoal.KNOWLEDGE

        return ProcessingGoal.GENERAL

    @staticmethod
    def _estimate_complexity(query: str) -> Complexity: 
     """
    Estimate the execution complexity for a normalized query.

    Parameters:
        query (str): Normalized query.

    Returns:
        Complexity

    Raises:
        None.

    Side Effects:
        None.
    """
     lowered = query.lower()

     if any(keyword in lowered for keyword in _HIGH_COMPLEXITY_KEYWORDS):
        return Complexity.HIGH

     if any(keyword in lowered for keyword in _MEDIUM_COMPLEXITY_KEYWORDS):
        return Complexity.MEDIUM

     return Complexity.LOW

    @staticmethod
    def _determine_resource_requirements(
    query: str,
    processing_goal: ProcessingGoal,
) -> ResourceRequirements:
     """
     Determine which ecosystem resources are required.

    Parameters:
        query (str):
            Normalized query.

        processing_goal (ProcessingGoal):
            Previously determined processing goal.

    Returns:
        ResourceRequirements

    Raises:
        None.

    Side Effects:
        None.
    """
     lowered = query.lower()

     knowledge = (
        processing_goal in {
            ProcessingGoal.KNOWLEDGE,
            ProcessingGoal.DOCUMENT,
            ProcessingGoal.CODE,
        }
        or lowered.startswith(_KNOWLEDGE_PREFIXES)
    )

     memory = any(
        keyword in lowered
        for keyword in _MEMORY_KEYWORDS
    )

     session = any(
        keyword in lowered
        for keyword in _SESSION_KEYWORDS
    )

     return ResourceRequirements(
        knowledge=knowledge,
        memory=memory,
        session=session,
    )

    @staticmethod
    def _build_decision_trace(
    processing_goal: ProcessingGoal,
    complexity: Complexity,
    resource_requirements: ResourceRequirements,
) -> DecisionTrace:
     """
    Build a deterministic DecisionTrace describing the Planner's
    decisions.

    Parameters:
        processing_goal (ProcessingGoal):
            The determined processing goal.

        complexity (Complexity):
            The estimated execution complexity.

        resource_requirements (ResourceRequirements):
            The required ecosystem resources.

    Returns:
        DecisionTrace

    Raises:
        None.

    Side Effects:
        None.
     """
     # ProcessingGoal explanation
     processing_goal_reasons = {
        ProcessingGoal.GENERAL:
            "The query does not require specialized processing.",

        ProcessingGoal.KNOWLEDGE:
            "The query requests factual or conceptual knowledge.",

        ProcessingGoal.MEMORY:
            "The query requests persistent user memory.",

        ProcessingGoal.SESSION:
            "The query depends on previous conversation context.",

        ProcessingGoal.DOCUMENT:
            "The query concerns a referenced document.",

        ProcessingGoal.CODE:
            "The query concerns source code.",
    }

     # Complexity explanation
     complexity_reasons = {
        Complexity.LOW:
            "The query requires straightforward analysis.",

        Complexity.MEDIUM:
            "The query requires moderate reasoning.",

        Complexity.HIGH:
            "The query requires complex reasoning.",
    }

     # Resource explanation
     required_resources = []

     if resource_requirements.knowledge:
        required_resources.append("knowledge")

     if resource_requirements.memory:
        required_resources.append("memory")

     if resource_requirements.session:
        required_resources.append("session")

     if required_resources:
        resource_reason = (
            "Required resources: "
            + ", ".join(required_resources)
            + "."
        )
     else:
        resource_reason = "No retrieval is required."

     return DecisionTrace(
        processing_goal_reason=processing_goal_reasons[
            processing_goal
        ],
        complexity_reason=complexity_reasons[
            complexity
        ],
        resource_requirements_reason=resource_reason,
    )