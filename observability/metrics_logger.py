"""Metrics Logger — Observability for Context Budgeting

Appends structured query metrics to logs/metrics.jsonl for offline analysis.
Each line is a JSON object with one query's complete lifecycle.

Fields logged:
    timestamp:         ISO-8601 timestamp
    query:             The user's question (truncated for privacy if needed)
    tokens_before:     Total context tokens before budgeting
    tokens_after:      Total context tokens after budgeting
    reduction_percent: (before - after) / before * 100
    knowledge_before, knowledge_after
    memory_before, memory_after
    session_before, session_after
    retrieval_latency_ms
    memory_latency_ms
    budget_latency_ms
    generation_latency_ms
    total_latency_ms

Usage:
    from observability.metrics_logger import metrics_logger
    metrics_logger.log({"query": "...", "tokens_before": 500, ...})

    # Or from rag.py after a query:
    from observability.metrics_logger import log_query_metrics
    log_query_metrics(query, metrics, latencies)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "metrics.jsonl"


# ---------------------------------------------------------------------------
# QueryMetrics dataclass
# ---------------------------------------------------------------------------

@dataclass
class QueryMetrics:
    """Standardized metrics for a single query."""

    # Identity
    timestamp: str = ""
    query: str = ""
    session_id: str = ""

    # Token counts
    tokens_before: int = 0
    tokens_after: int = 0
    reduction_percent: float = 0.0
    context_retained_percent: float = 0.0

    # Component breakdown
    knowledge_before: int = 0
    knowledge_after: int = 0
    memory_before: int = 0
    memory_after: int = 0
    session_before: int = 0
    session_after: int = 0

    # Question
    question_tokens: int = 0
    question_trimmed: bool = False

    # Latencies (milliseconds)
    retrieval_latency_ms: float = 0.0
    memory_latency_ms: float = 0.0
    budget_latency_ms: float = 0.0
    prompt_build_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    total_latency_ms: float = 0.0

    # Budget configuration
    total_budget: int = 0
    overhead_tokens: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# MetricsLogger
# ---------------------------------------------------------------------------

class MetricsLogger:
    """Thread-safe-ish (Python GIL) JSONL metrics appender."""

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or DEFAULT_LOG_FILE
        self._ensure_dir()

    def _ensure_dir(self):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, metrics: QueryMetrics | dict) -> None:
        """Append a single metrics record to the JSONL log."""
        if isinstance(metrics, QueryMetrics):
            record = metrics.to_dict()
        else:
            record = dict(metrics)

        # Ensure timestamp exists
        if "timestamp" not in record or not record["timestamp"]:
            record["timestamp"] = datetime.now(timezone.utc).isoformat()

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def log_raw(self, record: dict) -> None:
        """Append a raw dict (for backward compatibility or custom fields)."""
        if "timestamp" not in record or not record["timestamp"]:
            record["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def read_all(self) -> list[dict]:
        """Read all records from the log file."""
        if not self.log_file.exists():
            return []
        records = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def get_summary(self) -> dict:
        """Return aggregate statistics from all logged records."""
        records = self.read_all()
        if not records:
            return {"count": 0}

        total_queries = len(records)
        reductions = [r.get("reduction_percent", 0) for r in records]
        retained = [r.get("context_retained_percent", 0) for r in records]
        total_latencies = [r.get("total_latency_ms", 0) for r in records]
        budget_latencies = [r.get("budget_latency_ms", 0) for r in records]
        gen_latencies = [r.get("generation_latency_ms", 0) for r in records]

        trimmed_count = sum(1 for r in records if r.get("tokens_after", 0) < r.get("tokens_before", 0))

        return {
            "count": total_queries,
            "avg_reduction_percent": round(sum(reductions) / len(reductions), 2),
            "max_reduction_percent": round(max(reductions), 2),
            "min_reduction_percent": round(min(reductions), 2),
            "avg_context_retained_percent": round(sum(retained) / len(retained), 2),
            "trimmed_count": trimmed_count,
            "trimmed_percent": round(trimmed_count / total_queries * 100, 2),
            "avg_total_latency_ms": round(sum(total_latencies) / len(total_latencies), 2),
            "avg_budget_latency_ms": round(sum(budget_latencies) / len(budget_latencies), 2),
            "avg_generation_latency_ms": round(sum(gen_latencies) / len(gen_latencies), 2),
        }

    def clear(self) -> None:
        """Truncate the log file.  Use with caution."""
        if self.log_file.exists():
            self.log_file.write_text("", encoding="utf-8")


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

metrics_logger = MetricsLogger()


def log_query_metrics(
    query: str,
    budget_metrics,
    latencies: dict[str, float],
    session_id: str = "",
) -> None:
    """Convenience function to log a complete query from rag.py.

    Args:
        query: The user's question.
        budget_metrics: A BudgetMetrics object from ContextBudgeter.
        latencies: Dict with keys like "retrieval", "memory", "budget",
                   "prompt_build", "generation", "total" (values in seconds).
        session_id: Optional session identifier.
    """
    m = budget_metrics
    qm = QueryMetrics(
        query=query[:200],  # Truncate for log size
        session_id=session_id,
        tokens_before=m.total_before,
        tokens_after=m.total_after,
        reduction_percent=m.reduction_percent(),
        context_retained_percent=m.context_retained_percent(),
        knowledge_before=m.knowledge_before,
        knowledge_after=m.knowledge_after,
        memory_before=m.memory_before,
        memory_after=m.memory_after,
        session_before=m.session_before,
        session_after=m.session_after,
        question_tokens=m.question_tokens,
        question_trimmed=m.question_trimmed,
        retrieval_latency_ms=round(latencies.get("retrieval", 0) * 1000, 2),
        memory_latency_ms=round(latencies.get("memory", 0) * 1000, 2),
        budget_latency_ms=round(latencies.get("budget", 0) * 1000, 2),
        prompt_build_latency_ms=round(latencies.get("prompt_build", 0) * 1000, 2),
        generation_latency_ms=round(latencies.get("generation", 0) * 1000, 2),
        total_latency_ms=round(latencies.get("total", 0) * 1000, 2),
        total_budget=m.total_budget,
        overhead_tokens=m.overhead_tokens,
    )
    metrics_logger.log(qm)


def get_metrics_summary() -> dict:
    """Return aggregate statistics from the metrics log."""
    return metrics_logger.get_summary()
