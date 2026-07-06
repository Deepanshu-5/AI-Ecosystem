"""
budgeting/context_budgeter.py

Orchestrates deterministic, token-budget-compliant context allocation.
"""

from __future__ import annotations

from typing import Callable

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budget_validator import BudgetValidator
from budgeting.budgeted_context import BudgetedContext
from budgeting.exceptions import ContextBudgetOverflowError, ContextBudgetValidationError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext, SessionMessage

# Default category caps per frozen architecture
_DEFAULT_CAPS: dict[str, float] = {
    "knowledge": 0.60,
    "memory": 0.25,
    "session": 0.15,
}

_TRUNCATION_MARKER = " [...]"


class ContextBudgeter:
    """
    Transforms RetrievedContext into deterministic, token-budget-compliant
    structured context.

    Purpose:
        Owns budgeting orchestration: input validation, query token
        accounting, two-phase allocation, truncation, redistribution,
        output assembly, and output validation.

    Owned by:
        budgeting/context_budgeter.py

    Invariants:
        - Never retrieves context.
        - Never mutates RetrievedContext.
        - Never constructs prompts.
        - Deterministic for identical inputs.
    """

    def __init__(
        self,
        token_counter: Callable[[str], int] | None = None,
        token_truncator: Callable[[str, int], str] | None = None,
    ) -> None:
        """
        Initialise ContextBudgeter.

        Parameters:
            token_counter: Function that counts tokens in a string.
                If None, uses shared.token_counter.token_counter.count.
            token_truncator: Function that truncates text to max tokens.
                If None, uses shared.token_counter.token_counter.truncate.

        Returns:
            None.
        """
        if token_counter is None or token_truncator is None:
            from shared.token_counter import token_counter as _tc

            self._count_fn = token_counter if token_counter is not None else _tc.count
            self._truncate_fn = (
                token_truncator if token_truncator is not None else _tc.truncate
            )
        else:
            self._count_fn = token_counter
            self._truncate_fn = token_truncator

    def budget(
        self,
        retrieved_context: RetrievedContext,
        query: str,
        total_budget: int,
        reserved_budget: int,
        category_caps: dict[str, float] | None = None,
    ) -> BudgetedContext:
        """
        Execute the complete budgeting pipeline.

        Parameters:
            retrieved_context: The RetrievedContext to budget.
            query: The original user query.
            total_budget: Maximum token budget.
            reserved_budget: Tokens reserved for Prompt Builder.
            category_caps: Optional custom category caps. Must total 1.0.

        Returns:
            BudgetedContext: Validated, immutable budgeted context.

        Raises:
            ContextBudgetValidationError: If inputs are invalid.
            ContextBudgetOverflowError: If query budget <= 0.
        """
        # 1. Validate input
        BudgetValidator.validate_input(
            retrieved_context, query, total_budget, reserved_budget, category_caps
        )

        caps = category_caps if category_caps is not None else dict(_DEFAULT_CAPS)

        # 2. Query token accounting and overflow handling
        effective_query, query_tokens, query_truncated = self._handle_query(
            query, total_budget, reserved_budget
        )

        # 3. Calculate context budget
        context_budget = total_budget - reserved_budget - query_tokens
        if context_budget < 0:
            context_budget = 0

        # 4. Two-phase allocation
        phase1_result = self._phase1_allocate(retrieved_context, context_budget, caps)
        phase2_result = self._phase2_redistribute(
            retrieved_context,
            phase1_result,
            context_budget,
        )

        # 5. Build category contexts and metadata
        knowledge_ctx, knowledge_tokens = self._build_knowledge_context(
            phase2_result["knowledge"],
            retrieved_context.knowledge.metadata,
)
        memory_ctx, memory_tokens = self._build_memory_context(
            phase2_result["memory"],
            retrieved_context.memory.metadata,
)
        session_ctx, session_tokens = self._build_session_context(
            phase2_result["session"],
            retrieved_context.session.metadata,
)

        used_context_tokens = knowledge_tokens + memory_tokens + session_tokens
        remaining_tokens = context_budget - used_context_tokens
        if remaining_tokens < 0:
            remaining_tokens = 0

        truncated_unit_count = sum(
            1 for item in phase2_result["knowledge"] if item["truncated"]
        )
        truncated_unit_count += sum(
            1 for item in phase2_result["memory"] if item["truncated"]
        )
        truncated_unit_count += sum(
            1 for item in phase2_result["session"] if item["truncated"]
        )

        metadata = BudgetMetadata(
            total_budget=total_budget,
            reserved_tokens=reserved_budget,
            query_tokens=query_tokens,
            context_budget=context_budget,
            used_context_tokens=used_context_tokens,
            remaining_tokens=remaining_tokens,
            knowledge_tokens=knowledge_tokens,
            memory_tokens=memory_tokens,
            session_tokens=session_tokens,
            query_truncated=query_truncated,
            truncated_unit_count=truncated_unit_count,
        )

        budgeted = BudgetedContext(
            knowledge=knowledge_ctx,
            memory=memory_ctx,
            session=session_ctx,
            metadata=metadata,
            effective_query=effective_query,
        )

        # 6. Validate output
        BudgetValidator.validate_output(budgeted, context_budget, total_budget)
        return budgeted

    def _handle_query(
        self,
        query: str,
        total_budget: int,
        reserved_budget: int,
    ) -> tuple[str, int, bool]:
        """
        Handle query token counting and overflow.

        Returns:
            tuple: (effective_query, query_tokens, query_truncated)
        """
        query_tokens = self._count_fn(query)

        if query_tokens + reserved_budget <= total_budget:
            return query, query_tokens, False

        # Query overflow: truncate to available query budget
        query_budget = total_budget - reserved_budget
        if query_budget <= 0:
            raise ContextBudgetOverflowError(
                f"query_budget ({query_budget}) <= 0: cannot satisfy "
                f"query overflow policy"
            )

        truncated_query = self._truncate_with_marker(query, query_budget)
        truncated_tokens = self._count_fn(truncated_query)
        return truncated_query, truncated_tokens, True

    def _truncate_with_marker(self, text: str, max_tokens: int) -> str:
        """Truncate text while guaranteeing the final result fits max_tokens."""
        if max_tokens <= 0:
         return ""

        marker_tokens = self._count_fn(_TRUNCATION_MARKER)

        if marker_tokens > max_tokens:
            return self._truncate_fn(text, max_tokens)

        content_budget = max_tokens - marker_tokens

        while content_budget >= 0:
            truncated = self._truncate_fn(text, content_budget)
            result = truncated + _TRUNCATION_MARKER

            if self._count_fn(result) <= max_tokens:
                return result

            content_budget -= 1

        return self._truncate_fn(text, max_tokens)

    def _phase1_allocate(
        self,
        retrieved_context: RetrievedContext,
        context_budget: int,
        caps: dict[str, float],
    ) -> dict[str, list[dict]]:
        """
        Phase 1: Allocate within category caps.

        Returns:
            dict mapping category name to list of selected unit records.
            Each record has keys: "unit", "tokens", "truncated".
        """
        result: dict[str, list[dict]] = {
            "knowledge": [],
            "memory": [],
            "session": [],
        }

        # Calculate category budgets
        category_budgets = {
            cat: int(context_budget * cap)
            for cat, cap in caps.items()
        }

        # Knowledge
        cat_budget = category_budgets["knowledge"]
        for item in retrieved_context.knowledge.items:
            record = self._try_select_unit(
                item.text,
                cat_budget,
                allow_truncation=False,
            )
            if record is not None:
                result["knowledge"].append(
                    {
                        "unit": item,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                    }
                )
                cat_budget -= record["tokens"]

        # Memory
        cat_budget = category_budgets["memory"]
        for entry in retrieved_context.memory.entries:
            record = self._try_select_unit(entry.content, cat_budget, allow_truncation=False)
            if record is not None:
                result["memory"].append(
                    {
                        "unit": entry,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                    }
                )
                cat_budget -= record["tokens"]

        # Session: summary first, then messages
        cat_budget = category_budgets["session"]
        summary = retrieved_context.session.summary
        if summary:
            record = self._try_select_unit(summary, cat_budget, allow_truncation=False)
            if record is not None:
                result["session"].append(
                    {
                        "unit": "summary",
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                        "summary": True,
                    }
                )
                cat_budget -= record["tokens"]

        for msg in retrieved_context.session.recent_messages:
            record = self._try_select_unit(msg.content, cat_budget, allow_truncation=False)
            if record is not None:
                result["session"].append(
                    {
                        "unit": msg,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                        "summary": False,
                    }
                )
                cat_budget -= record["tokens"]

        return result

    def _phase2_redistribute(
        self,
        retrieved_context: RetrievedContext,
        phase1_result: dict[str, list[dict]],
        context_budget: int,
    ) -> dict[str, list[dict]]:
        """
        Phase 2: Redistribute unused budget.

        Returns:
            Final allocation with redistributed units included.
        """
        result = {
            "knowledge": list(phase1_result["knowledge"]),
            "memory": list(phase1_result["memory"]),
            "session": list(phase1_result["session"]),
        }

        used = (
            sum(r["tokens"] for r in result["knowledge"])
            + sum(r["tokens"] for r in result["memory"])
            + sum(r["tokens"] for r in result["session"])
        )
        remaining_budget = context_budget - used
        if remaining_budget <= 0:
            return result

        # Track which original items are already selected by identity
        selected_knowledge_ids = {id(r["unit"]) for r in result["knowledge"]}
        selected_memory_ids = {id(r["unit"]) for r in result["memory"]}
        selected_session_ids = set()
        for r in result["session"]:
            if r.get("summary"):
                selected_session_ids.add("__summary__")
            else:
                selected_session_ids.add(id(r["unit"]))

        # Knowledge redistribution
        for item in retrieved_context.knowledge.items:
            if id(item) in selected_knowledge_ids:
                continue
            record = self._try_select_unit(item.text, remaining_budget, allow_truncation=True)
            if record is not None:
                result["knowledge"].append(
                    {
                        "unit": item,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                    }
                )
                remaining_budget -= record["tokens"]
                selected_knowledge_ids.add(id(item))

        # Memory redistribution
        for entry in retrieved_context.memory.entries:
            if id(entry) in selected_memory_ids:
                continue
            record = self._try_select_unit(entry.content, remaining_budget,allow_truncation=True)
            if record is not None:
                result["memory"].append(
                    {
                        "unit": entry,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                    }
                )
                remaining_budget -= record["tokens"]
                selected_memory_ids.add(id(entry))

        # Session redistribution
        summary = retrieved_context.session.summary
        if summary and "__summary__" not in selected_session_ids:
            record = self._try_select_unit(summary, remaining_budget,allow_truncation=True)
            if record is not None:
                result["session"].append(
                    {
                        "unit": "summary",
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                        "summary": True,
                    }
                )
                remaining_budget -= record["tokens"]
                selected_session_ids.add("__summary__")

        for msg in retrieved_context.session.recent_messages:
            if id(msg) in selected_session_ids:
                continue
            record = self._try_select_unit(msg.content, remaining_budget, allow_truncation=True)
            if record is not None:
                result["session"].append(
                    {
                        "unit": msg,
                        "tokens": record["tokens"],
                        "truncated": record["truncated"],
                        "text": record["text"],
                        "summary": False,
                    }
                )
                remaining_budget -= record["tokens"]
                selected_session_ids.add(id(msg))

        return result

    def _try_select_unit(
    self,
    text: str,
    budget: int,
    *,
    allow_truncation: bool,
) -> dict[str, object] | None:
        """
        Try to select a unit within the given budget.

        Returns a record with "tokens", "truncated", "text" if selected,
        or None if the unit cannot fit.
        """
        if budget <= 0:
            return None

        tokens = self._count_fn(text)
        if tokens <= budget:
            return {"tokens": tokens, "truncated": False, "text": text}
        if not allow_truncation:
            return None
        # Try truncation
        truncated = self._truncate_with_marker(text, budget)
        truncated_tokens = self._count_fn(truncated)
        if truncated_tokens <= budget and truncated.strip():
            return {
                "tokens": truncated_tokens,
                "truncated": True,
                "text": truncated,
            }

        return None

    def _build_knowledge_context(
        self,
        records: list[dict],
        metadata: dict[str, object],
) -> tuple[KnowledgeContext, int]:
        """Build KnowledgeContext from selected records."""
        items: list[KnowledgeItem] = []
        total_tokens = 0
        for record in records:
            unit = record["unit"]
            text = record["text"]
            if record["truncated"]:
                # Create new item preserving metadata
                items.append(
                    KnowledgeItem(
                        text=text,
                        source=unit.source,
                        score=unit.score,
                    )
                )
            else:
                items.append(unit)
            total_tokens += record["tokens"]
        return (
            KnowledgeContext(
                items=tuple(items),
                 metadata=dict(metadata),
        ),
        total_tokens,
    )

    def _build_memory_context(
       self,
       records: list[dict],
       metadata: dict[str, object],
    ) -> tuple[MemoryContext, int]:
        """Build MemoryContext from selected records."""
        entries: list[MemoryEntry] = []
        total_tokens = 0
        for record in records:
            unit = record["unit"]
            text = record["text"]
            if record["truncated"]:
                entries.append(
                    MemoryEntry(
                        content=text,
                        memory_id=unit.memory_id,
                        score=unit.score,
                    )
                )
            else:
                entries.append(unit)
            total_tokens += record["tokens"]
        return (
            MemoryContext(
               entries=tuple(entries),
               metadata=dict(metadata),
            ),
            total_tokens,
        )

    def _build_session_context(
       self,
       records: list[dict],
       metadata: dict[str, object],
    ) -> tuple[SessionContext, int]:
        """Build SessionContext from selected records."""
        summary = ""
        messages: list[SessionMessage] = []
        total_tokens = 0

        for record in records:
            if record.get("summary"):
                summary = record["text"]
            else:
                unit = record["unit"]
                text = record["text"]
                if record["truncated"]:
                    messages.append(
                        SessionMessage(role=unit.role, content=text)
                    )
                else:
                    messages.append(unit)
            total_tokens += record["tokens"]

        return (
            SessionContext(
                summary=summary,
                recent_messages=tuple(messages),
                metadata=dict(metadata),
            ),
            total_tokens,
        )
