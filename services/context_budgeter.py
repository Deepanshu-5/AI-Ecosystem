"""Context Budgeting Layer v2.0

Category-budget allocation with priority redistribution, ContextItem abstraction,
and query overflow protection.

Architecture:
    Knowledge  cap = 60% of available context tokens
    Memory     cap = 25% of available context tokens
    Session    cap = 15% of available context tokens

Spare budget from lower-priority categories is redistributed to higher-priority
categories that hit their cap.  This prevents knowledge starvation of memory
and session while still allowing flexibility when categories don't need their
full allocation.

Usage (legacy string API — still supported):
    from services.context_budgeter import get_budgeter
    budgeter = get_budgeter()
    result = budgeter.build_context(
        question="...",
        knowledge_context="...",
        memory_context="...",
        conversation_summary="...",
        recent_messages="..."
    )

Usage (future ContextItem API):
    from services.context_budgeter import ContextItem, ContextBudgeter
    items = [
        ContextItem(text="...", source="knowledge", priority=1, score=0.9),
        ContextItem(text="...", source="memory", priority=2, score=0.7),
    ]
    result = budgeter.build_context_from_items(question="...", items=items)
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Optional

from shared.token_counter import token_counter


# ---------------------------------------------------------------------------
# ContextItem abstraction (future-proof data structure)
# ---------------------------------------------------------------------------

@dataclass
class ContextItem:
    """A single piece of context with metadata.

    Migration plan:
    1.  Define ContextItem here (done).
    2.  Update retrieval/retriever.py to return ContextItem list instead of
        raw Document objects.  Document already has text, metadata, score —
        map to ContextItem.source="knowledge", priority=1.
    3.  Update memory/memory_service.py recall() to return ContextItem list
        with source="memory", priority=2.
    4.  Update conversation_memory/session_memory.py get_session_context() to
        return ContextItem objects with source="session_summary" or
        "recent_messages", priority=3 or 4.
    5.  Update services/context_formatter.py to accept ContextItem list.
    6.  Update llm/rag.py to pass ContextItem lists into budgeter.
    7.  Remove legacy string-based build_context() after full migration.

    Fields:
        text:        Raw content.
        source:      "knowledge" | "memory" | "session_summary" | "recent_messages" | "tool" | "user"
        priority:    1 = highest (knowledge), 4 = lowest (supporting info).
        score:       Relevance score from retrieval/reranking (0.0–1.0+).
        token_count: Pre-computed token count.  Computed lazily if 0.
        timestamp:   Unix timestamp of creation or retrieval.
        metadata:    Extra key-value pairs (source file, chunk index, etc.).
    """

    text: str
    source: str
    priority: int = 4
    score: float = 0.0
    token_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.token_count == 0 and self.text:
            self.token_count = token_counter.count(self.text)

    @property
    def category(self) -> str:
        """Map source to budget category."""
        mapping = {
            "knowledge": "knowledge",
            "memory": "memory",
            "session_summary": "session",
            "recent_messages": "session",
            "tool": "tool",
            "user": "user",
        }
        return mapping.get(self.source, "other")


# ---------------------------------------------------------------------------
# BudgetMetrics (observability)
# ---------------------------------------------------------------------------

@dataclass
class BudgetMetrics:
    """Observability metrics for a single budgeting operation."""

    total_budget: int = 0
    overhead_tokens: int = 0
    question_tokens: int = 0
    question_original_tokens: int = 0
    question_trimmed: bool = False
    question_original: str = ""
    question_after: str = ""
    available_tokens: int = 0
    min_context_budget: int = 0

    knowledge_before: int = 0
    knowledge_after: int = 0
    knowledge_cap: int = 0
    memory_before: int = 0
    memory_after: int = 0
    memory_cap: int = 0
    session_before: int = 0
    session_after: int = 0
    session_cap: int = 0

    total_before: int = 0
    total_after: int = 0
    trimmed: bool = False
    spare_redistributed: int = 0
    budget_latency_ms: float = 0.0

    def reduction_percent(self) -> float:
        if self.total_before == 0:
            return 0.0
        return round((1 - self.total_after / self.total_before) * 100, 2)

    def context_retained_percent(self) -> float:
        if self.total_before == 0:
            return 100.0
        return round(self.total_after / self.total_before * 100, 2)

    def report(self) -> str:
        q_info = f"{self.question_tokens}"
        if self.question_trimmed:
            q_info += f" (trimmed from {self.question_original_tokens})"
        lines = [
            f"[BUDGET] Total budget: {self.total_budget}",
            f"[BUDGET] Prompt overhead: {self.overhead_tokens}",
            f"[BUDGET] Question tokens: {q_info}",
            f"[BUDGET] Question trimmed: {self.question_trimmed}",
            f"[BUDGET] Available for context: {self.available_tokens}",
            f"[BUDGET] Knowledge: {self.knowledge_before} -> {self.knowledge_after} (cap={self.knowledge_cap})",
            f"[BUDGET] Memory: {self.memory_before} -> {self.memory_after} (cap={self.memory_cap})",
            f"[BUDGET] Session: {self.session_before} -> {self.session_after} (cap={self.session_cap})",
            f"[BUDGET] Total context: {self.total_before} -> {self.total_after}",
            f"[BUDGET] Reduction: {self.reduction_percent()}%",
            f"[BUDGET] Context retained: {self.context_retained_percent()}%",
        ]
        if self.trimmed:
            lines.append("[BUDGET] Context was trimmed to fit budget.")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_budget": self.total_budget,
            "overhead_tokens": self.overhead_tokens,
            "question_tokens": self.question_tokens,
            "question_original_tokens": self.question_original_tokens,
            "question_trimmed": self.question_trimmed,
            "available_tokens": self.available_tokens,
            "knowledge_before": self.knowledge_before,
            "knowledge_after": self.knowledge_after,
            "knowledge_cap": self.knowledge_cap,
            "memory_before": self.memory_before,
            "memory_after": self.memory_after,
            "memory_cap": self.memory_cap,
            "session_before": self.session_before,
            "session_after": self.session_after,
            "session_cap": self.session_cap,
            "total_before": self.total_before,
            "total_after": self.total_after,
            "trimmed": self.trimmed,
            "reduction_percent": self.reduction_percent(),
            "context_retained_percent": self.context_retained_percent(),
            "spare_redistributed": self.spare_redistributed,
            "budget_latency_ms": self.budget_latency_ms,
        }


# ---------------------------------------------------------------------------
# Context Budgeter
# ---------------------------------------------------------------------------

class ContextBudgeter:
    """Priority-based context budget allocator with category caps.

    Prevents higher-priority categories from starving lower-priority ones
    by enforcing maximum percentages per category, then redistributing
    unused budget upward in priority order.
    """

    DEFAULT_OVERHEAD_TOKENS = 60
    MIN_CONTEXT_BUDGET = 50  # Minimum tokens we reserve for context
    MAX_QUESTION_FRACTION = 0.50  # Question may consume at most 50% of total budget

    # Category caps as fractions of *available* context budget (after question + overhead).
    # These must sum to 1.0 (100%).
    DEFAULT_CATEGORY_CAPS: dict[str, float] = {
        "knowledge": 0.60,
        "memory": 0.25,
        "session": 0.15,
    }

    def __init__(
        self,
        total_budget: int = 2048,
        overhead_tokens: Optional[int] = None,
        category_caps: Optional[dict[str, float]] = None,
    ):
        self.total_budget = total_budget
        self.overhead_tokens = (
            overhead_tokens if overhead_tokens is not None else self.DEFAULT_OVERHEAD_TOKENS
        )
        self.category_caps = category_caps or dict(self.DEFAULT_CATEGORY_CAPS)
        self._validate_caps()
        self.counter = token_counter

    def _validate_caps(self):
        total = sum(self.category_caps.values())
        if not 0.99 <= total <= 1.01:
            raise ValueError(
                f"Category caps must sum to 1.0, got {total}. "
                f"Caps: {self.category_caps}"
            )

    # ------------------------------------------------------------------
    # Legacy string-based API (backward compatible)
    # ------------------------------------------------------------------

    def build_context(
        self,
        question: str,
        knowledge_context: str = "",
        memory_context: str = "",
        conversation_summary: str = "",
        recent_messages: str = "",
    ) -> dict:
        """Trim context components to fit within the token budget.

        Returns a dict compatible with ``llm.prompt_builder.build_prompt``,
        plus a ``metrics`` key for observability.
        """
        budget_start = time.perf_counter()

        # 1. Handle question overflow
        question_out, q_metrics = self._handle_question_overflow(question)
        metrics = BudgetMetrics()
        metrics.total_budget = self.total_budget
        metrics.overhead_tokens = self.overhead_tokens
        metrics.question_tokens = q_metrics["tokens_after"]
        metrics.question_original_tokens = q_metrics["tokens_before"]
        metrics.question_trimmed = q_metrics["trimmed"]
        metrics.question_original = question
        metrics.question_after = question_out
        metrics.min_context_budget = self.MIN_CONTEXT_BUDGET

        available = self.total_budget - self.overhead_tokens - q_metrics["tokens_after"]
        available = max(available, self.MIN_CONTEXT_BUDGET)
        metrics.available_tokens = available

        # 2. Map string components to category tokens
        category_tokens = {
            "knowledge": self.counter.count(knowledge_context),
            "memory": self.counter.count(memory_context),
            "session": self.counter.count(conversation_summary) + self.counter.count(recent_messages),
        }

        # 3. Allocate with category caps
        allocations = self._allocate_with_caps(category_tokens, available)

        # 4. Trim each component to its allocated budget
        knowledge_out = self._trim_to(knowledge_context, allocations["knowledge"])
        memory_out = self._trim_to(memory_context, allocations["memory"])

        # Session budget split: summary first, then recent messages
        session_budget = allocations["session"]
        summary_tokens = self.counter.count(conversation_summary)
        recent_tokens = self.counter.count(recent_messages)
        total_session_requested = summary_tokens + recent_tokens

        if total_session_requested <= session_budget or total_session_requested == 0:
            summary_out = conversation_summary
            recent_out = recent_messages
        else:
            # Give summary priority within session budget
            summary_alloc = min(summary_tokens, session_budget)
            summary_out = self._trim_to(conversation_summary, summary_alloc)
            remaining = session_budget - self.counter.count(summary_out)
            recent_out = self._trim_to(recent_messages, max(remaining, 0))

        # 5. Populate metrics
        metrics.knowledge_before = category_tokens["knowledge"]
        metrics.knowledge_after = self.counter.count(knowledge_out)
        metrics.knowledge_cap = int(available * self.category_caps["knowledge"])
        metrics.memory_before = category_tokens["memory"]
        metrics.memory_after = self.counter.count(memory_out)
        metrics.memory_cap = int(available * self.category_caps["memory"])
        metrics.session_before = total_session_requested
        metrics.session_after = self.counter.count(summary_out) + self.counter.count(recent_out)
        metrics.session_cap = int(available * self.category_caps["session"])
        metrics.total_before = sum(category_tokens.values())
        metrics.total_after = (
            metrics.knowledge_after + metrics.memory_after + metrics.session_after
        )
        metrics.trimmed = metrics.total_after < metrics.total_before
        metrics.spare_redistributed = allocations.get("spare_redistributed", 0)
        metrics.budget_latency_ms = round((time.perf_counter() - budget_start) * 1000, 2)

        return {
            "question": question_out,
            "knowledge_context": knowledge_out,
            "memory_context": memory_out,
            "conversation_summary": summary_out,
            "recent_messages": recent_out,
            "metrics": metrics,
        }

    # ------------------------------------------------------------------
    # Future ContextItem API
    # ------------------------------------------------------------------

    def build_context_from_items(
        self,
        question: str,
        items: list[ContextItem],
    ) -> dict:
        """Budget context using ContextItem list (future API).

        Groups items by category, sorts within each category by score (desc),
        then applies category caps.
        """
        budget_start = time.perf_counter()

        # 1. Handle question overflow
        question_out, q_metrics = self._handle_question_overflow(question)
        metrics = BudgetMetrics()
        metrics.total_budget = self.total_budget
        metrics.overhead_tokens = self.overhead_tokens
        metrics.question_tokens = q_metrics["tokens_after"]
        metrics.question_original_tokens = q_metrics["tokens_before"]
        metrics.question_trimmed = q_metrics["trimmed"]
        metrics.available_tokens = max(
            self.total_budget - self.overhead_tokens - q_metrics["tokens_after"],
            self.MIN_CONTEXT_BUDGET,
        )
        available = metrics.available_tokens

        # 2. Group by category, sort by score descending
        from collections import defaultdict

        by_category: dict[str, list[ContextItem]] = defaultdict(list)
        for item in items:
            by_category[item.category].append(item)

        for cat in by_category:
            by_category[cat].sort(key=lambda x: x.score, reverse=True)

        # 3. Compute requested tokens per category
        category_tokens = {
            cat: sum(it.token_count for it in by_category.get(cat, []))
            for cat in self.category_caps
        }

        # 4. Allocate with caps
        allocations = self._allocate_with_caps(category_tokens, available)

        # 5. Trim items within each category
        result_items: list[ContextItem] = []
        for cat, cap in allocations.items():
            if cat == "spare_redistributed":
                continue
            cat_items = by_category.get(cat, [])
            trimmed = self._trim_items(cat_items, cap)
            result_items.extend(trimmed)

        # 6. Metrics
        total_before = sum(category_tokens.values())
        total_after = sum(it.token_count for it in result_items)

        metrics.knowledge_before = category_tokens.get("knowledge", 0)
        metrics.knowledge_after = sum(
            it.token_count for it in result_items if it.category == "knowledge"
        )
        metrics.knowledge_cap = int(available * self.category_caps["knowledge"])
        metrics.memory_before = category_tokens.get("memory", 0)
        metrics.memory_after = sum(
            it.token_count for it in result_items if it.category == "memory"
        )
        metrics.memory_cap = int(available * self.category_caps["memory"])
        metrics.session_before = category_tokens.get("session", 0)
        metrics.session_after = sum(
            it.token_count for it in result_items if it.category == "session"
        )
        metrics.session_cap = int(available * self.category_caps["session"])
        metrics.total_before = total_before
        metrics.total_after = total_after
        metrics.trimmed = total_after < total_before
        metrics.spare_redistributed = allocations.get("spare_redistributed", 0)
        metrics.budget_latency_ms = round((time.perf_counter() - budget_start) * 1000, 2)

        return {
            "question": question_out,
            "items": result_items,
            "metrics": metrics,
        }

    # ------------------------------------------------------------------
    # Internal allocation engine
    # ------------------------------------------------------------------

    def _allocate_with_caps(
        self, category_tokens: dict[str, int], available: int
    ) -> dict[str, int]:
        """Two-phase allocation:
        Phase 1: Cap each category at its percentage of available.
        Phase 2: Redistribute unused budget from lower-priority categories
                 to higher-priority categories that hit their cap.

        Priority order: knowledge (1) > memory (2) > session (3)
        """
        priority_order = ["knowledge", "memory", "session"]

        # Phase 1: Cap allocation
        allocated = {}
        for cat in priority_order:
            cap = int(available * self.category_caps[cat])
            requested = category_tokens.get(cat, 0)
            allocated[cat] = min(requested, cap)

        total_allocated = sum(allocated.values())

        # Fast path: everything fits within available
        if total_allocated <= available:
            # We may still have room to give categories their full requested amount
            spare = available - total_allocated

            # Phase 2: Redistribute spare upward in priority order
            redistributed = 0
            for cat in priority_order:
                deficit = category_tokens.get(cat, 0) - allocated[cat]
                if deficit > 0 and spare > 0:
                    extra = min(deficit, spare)
                    allocated[cat] += extra
                    spare -= extra
                    redistributed += extra

            allocated["spare_redistributed"] = redistributed
            return allocated

        # Hard trim path: total allocated > available (shouldn't happen with caps summing to 1.0,
        # but handle edge cases like rounding)
        scale = available / total_allocated if total_allocated > 0 else 1.0
        for cat in priority_order:
            allocated[cat] = int(allocated[cat] * scale)

        allocated["spare_redistributed"] = 0
        return allocated

    # ------------------------------------------------------------------
    # Question overflow handling
    # ------------------------------------------------------------------

    def _handle_question_overflow(self, question: str) -> tuple[str, dict]:
        """Handle the case where the question itself exceeds budget.

        Strategy (Option B: Truncate with safety):
        1.  max_question_budget = min(total_budget - overhead - MIN_CONTEXT, total * 0.5)
        2.  If question fits: pass through unchanged.
        3.  If question exceeds: truncate to max_question_budget, emit warning.
        4.  If even truncated question leaves < MIN_CONTEXT: hard cap.

        Returns (trimmed_question, {"tokens_before": N, "tokens_after": N, "trimmed": bool})
        """
        tokens_before = self.counter.count(question)
        max_question_budget = min(
            self.total_budget - self.overhead_tokens - self.MIN_CONTEXT_BUDGET,
            int(self.total_budget * self.MAX_QUESTION_FRACTION),
        )
        max_question_budget = max(max_question_budget, 0)

        if tokens_before <= max_question_budget:
            return question, {
                "tokens_before": tokens_before,
                "tokens_after": tokens_before,
                "trimmed": False,
            }

        # Question exceeds budget — truncate
        trimmed = self.counter.truncate(question, max_question_budget)
        tokens_after = self.counter.count(trimmed)

        warnings.warn(
            f"[QUERY OVERFLOW] Question ({tokens_before} tokens) exceeds "
            f"max_question_budget ({max_question_budget}). Truncated to "
            f"{tokens_after} tokens. Consider splitting the query.",
            stacklevel=3,
        )

        return trimmed, {
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "trimmed": True,
        }

    # ------------------------------------------------------------------
    # Trimming helpers
    # ------------------------------------------------------------------

    def _trim_to(self, text: str, max_tokens: int) -> str:
        """Trim text to fit within max_tokens."""
        if not text or not text.strip():
            return ""
        if self.counter.count(text) <= max_tokens:
            return text
        truncated = self.counter.truncate(text, max_tokens)
        if not truncated.rstrip().endswith("[...]"):
            truncated = truncated.rstrip() + " [...]"
        return truncated

    def _trim_items(self, items: list[ContextItem], max_tokens: int) -> list[ContextItem]:
        """Trim a list of ContextItems to fit within max_tokens, preserving
        highest-score items first."""
        if not items:
            return []

        result = []
        used = 0
        for item in items:
            if used + item.token_count <= max_tokens:
                result.append(item)
                used += item.token_count
            else:
                # Try to fit a partial of the last item
                remaining = max_tokens - used
                if remaining > 10:  # Minimum meaningful chunk
                    trimmed_text = self._trim_to(item.text, remaining)
                    if trimmed_text:
                        trimmed_item = ContextItem(
                            text=trimmed_text,
                            source=item.source,
                            priority=item.priority,
                            score=item.score,
                            token_count=self.counter.count(trimmed_text),
                            timestamp=item.timestamp,
                            metadata=item.metadata,
                        )
                        result.append(trimmed_item)
                break
        return result


# ---------------------------------------------------------------------------
# Convenience factory using project settings
# ---------------------------------------------------------------------------

def get_budgeter(
    total_budget: Optional[int] = None,
    overhead_tokens: Optional[int] = None,
    category_caps: Optional[dict[str, float]] = None,
) -> ContextBudgeter:
    """Create a budgeter from settings or explicit overrides."""
    try:
        from config.settings import (
            CONTEXT_BUDGET_TOTAL,
            CONTEXT_BUDGET_OVERHEAD,
            CONTEXT_CATEGORY_CAPS,
        )
    except Exception:
        CONTEXT_BUDGET_TOTAL = 2048
        CONTEXT_BUDGET_OVERHEAD = 60
        CONTEXT_CATEGORY_CAPS = None

    budget = total_budget if total_budget is not None else CONTEXT_BUDGET_TOTAL
    overhead = overhead_tokens if overhead_tokens is not None else (
        CONTEXT_BUDGET_OVERHEAD if CONTEXT_BUDGET_OVERHEAD is not None else None
    )
    caps = category_caps if category_caps is not None else CONTEXT_CATEGORY_CAPS
    return ContextBudgeter(total_budget=budget, overhead_tokens=overhead, category_caps=caps)
