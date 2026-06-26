"""Budgeting Evaluation Script

Runs synthetic queries through the ContextBudgeter with realistic context sizes
and measures token reduction, latency, fairness, and context retention.

Usage:
    python evaluation/evaluate_budgeting.py

Output:
    evaluation/report.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median

import sys
root = str(Path(__file__).resolve().parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)

from services.context_budgeter import ContextBudgeter, get_budgeter, ContextItem
from shared.token_counter import token_counter


# ---------------------------------------------------------------------------
# Test fixtures — realistic context sizes
# ---------------------------------------------------------------------------

# Based on actual project measurements:
# - chunk_size = 500 chars
# - final_context_chunks = 2
# - So typical knowledge context ≈ 2 * 500 = 1000 chars ≈ 250–300 tokens
# - Memory: typically 1–3 items, each ~50–150 tokens
# - Session: summary ~30–80 tokens, recent messages ~50–200 tokens

SMALL_KNOWLEDGE = "Paris is the capital of France. It is known for the Eiffel Tower. "
MEDIUM_KNOWLEDGE = (
    "Paris is the capital of France. It is known for the Eiffel Tower and the Louvre. "
    "The city has a population of over 2 million people. It is a major global center for art, "
    "fashion, gastronomy, and culture. The Seine River runs through it. " * 5
)
LARGE_KNOWLEDGE = (
    "The French Revolution was a period of radical political and societal change in France "
    "that began with the Estates General of 1789 and ended with the formation of the French "
    "Consulate in November 1799. Many of its ideas are considered fundamental principles of "
    "liberal democracy, while the values and institutions it created remain central to French "
    "political discourse. The Revolution resulted in the suppression of the feudal system, "
    "the emancipation of the Catholic Church, the adoption of the Declaration of the Rights "
    "of Man and of the Citizen, and a new civil legal code. " * 20
)

SMALL_MEMORY = "User likes French history. User prefers concise answers."
MEDIUM_MEMORY = (
    "User likes French history. User prefers concise answers. "
    "User previously asked about the French Revolution. User is a software developer. "
    "User works with Python and ChromaDB. User is building an AI ecosystem. "
)
LARGE_MEMORY = (
    "User likes French history. User prefers concise answers. "
    "User previously asked about the French Revolution. User is a software developer. "
    "User works with Python and ChromaDB. User is building an AI ecosystem. "
    "User's hardware is Intel i7-13620H with 16GB RAM. User uses Windows. "
    "User prefers local CPU inference. User's default model is qwen2.5:1.5b. "
    "User values token efficiency over model size. User has a ChromaDB instance running. "
    "User's project is in D:\\ai-ecosystem. User likes Markdown documentation. "
    "User prefers incremental improvements over big rewrites. User values measurements. "
) * 3

SMALL_SESSION_SUMMARY = "Discussing European capitals."
MEDIUM_SESSION_SUMMARY = (
    "We discussed European capitals, then moved to the French Revolution. "
    "User asked about Paris landmarks and French political history. "
)
LARGE_SESSION_SUMMARY = (
    "We discussed European capitals, then moved to the French Revolution. "
    "User asked about Paris landmarks and French political history. "
    "The conversation covered the Estates General, the Declaration of Rights, "
    "Napoleon, the Consulate, and the modern French Republic. "
    "User showed interest in the timeline of major events. "
) * 5

SMALL_RECENT = "user: What is the capital of France?"
MEDIUM_RECENT = (
    "user: What is the capital of France?\n"
    "assistant: Paris is the capital of France.\n"
    "user: Tell me about the French Revolution.\n"
    "assistant: The French Revolution began in 1789."
)
LARGE_RECENT = (
    "user: What is the capital of France?\n"
    "assistant: Paris is the capital of France.\n"
    "user: Tell me about the French Revolution.\n"
    "assistant: The French Revolution began in 1789 and ended in 1799.\n"
    "user: What were the major causes?\n"
    "assistant: Financial crisis, social inequality, and Enlightenment ideas.\n"
    "user: Who were the key figures?\n"
    "assistant: Robespierre, Marat, Danton, and Napoleon.\n"
    "user: What happened to the monarchy?\n"
    "assistant: Louis XVI was executed in 1793. The monarchy was abolished.\n"
) * 3


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    name: str
    question: str
    knowledge: str
    memory: str
    summary: str
    recent: str
    expected_behavior: str = ""


TEST_CASES = [
    # 1. Small everything — should fit without trimming
    TestCase(
        name="small_all_fits",
        question="What is the capital of France?",
        knowledge=SMALL_KNOWLEDGE,
        memory=SMALL_MEMORY,
        summary=SMALL_SESSION_SUMMARY,
        recent=SMALL_RECENT,
        expected_behavior="No trimming. All categories at 100%.",
    ),
    # 2. Medium everything — should fit or lightly trim
    TestCase(
        name="medium_all",
        question="Tell me about the French Revolution and its major events.",
        knowledge=MEDIUM_KNOWLEDGE,
        memory=MEDIUM_MEMORY,
        summary=MEDIUM_SESSION_SUMMARY,
        recent=MEDIUM_RECENT,
        expected_behavior="Light trimming possible. Knowledge dominates.",
    ),
    # 3. Large knowledge, small rest — tests knowledge starvation prevention
    TestCase(
        name="large_knowledge_starvation_test",
        question="Explain the French Revolution in detail.",
        knowledge=LARGE_KNOWLEDGE,
        memory=SMALL_MEMORY,
        summary=SMALL_SESSION_SUMMARY,
        recent=SMALL_RECENT,
        expected_behavior="Knowledge capped at 60%. Memory and session preserved at 25%/15%.",
    ),
    # 4. Large memory, small rest — tests memory starvation prevention
    TestCase(
        name="large_memory_starvation_test",
        question="What do I like?",
        knowledge=SMALL_KNOWLEDGE,
        memory=LARGE_MEMORY,
        summary=SMALL_SESSION_SUMMARY,
        recent=SMALL_RECENT,
        expected_behavior="Memory capped at 25%. Knowledge gets 60%. Session gets 15%.",
    ),
    # 5. Large session, small rest — tests session starvation prevention
    TestCase(
        name="large_session_starvation_test",
        question="Continue our previous discussion.",
        knowledge=SMALL_KNOWLEDGE,
        memory=SMALL_MEMORY,
        summary=LARGE_SESSION_SUMMARY,
        recent=LARGE_RECENT,
        expected_behavior="Session capped at 15%. Knowledge gets 60%. Memory gets 25%.",
    ),
    # 6. Everything large — heavy trimming across all categories
    TestCase(
        name="everything_large",
        question="Give me a comprehensive overview of French history from the Revolution to modern times, including all major figures, events, and political changes.",
        knowledge=LARGE_KNOWLEDGE,
        memory=LARGE_MEMORY,
        summary=LARGE_SESSION_SUMMARY,
        recent=LARGE_RECENT,
        expected_behavior="All categories trimmed. Knowledge 60%, Memory 25%, Session 15%.",
    ),
    # 7. Query overflow — very long question
    TestCase(
        name="query_overflow",
        question=(
            "I need you to write a very detailed and comprehensive essay about the French Revolution "
            "covering every single aspect from the financial crisis to the Reign of Terror to Napoleon "
            "and the aftermath. Please include all dates, all names, all events, and all consequences. "
            "Make it extremely thorough and leave nothing out. This should be a complete historical "
            "treatment suitable for a PhD thesis. " * 50
        ),
        knowledge=SMALL_KNOWLEDGE,
        memory=SMALL_MEMORY,
        summary=SMALL_SESSION_SUMMARY,
        recent=SMALL_RECENT,
        expected_behavior="Question truncated to 50% of budget. Context preserved.",
    ),
    # 8. Empty context — minimal test
    TestCase(
        name="empty_context",
        question="Hello",
        knowledge="",
        memory="",
        summary="",
        recent="",
        expected_behavior="Zero context. Fast path.",
    ),
    # 9. Only knowledge, no memory/session
    TestCase(
        name="knowledge_only",
        question="What is Paris?",
        knowledge=MEDIUM_KNOWLEDGE,
        memory="",
        summary="",
        recent="",
        expected_behavior="Knowledge gets full 60% + spare from memory/session. No trimming if fits.",
    ),
    # 10. Only memory, no knowledge
    TestCase(
        name="memory_only",
        question="What do I like?",
        knowledge="",
        memory=MEDIUM_MEMORY,
        summary="",
        recent="",
        expected_behavior="Memory gets full 25% + spare from knowledge/session. No trimming if fits.",
    ),
]


# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    test_name: str
    expected_behavior: str

    knowledge_before: int = 0
    knowledge_after: int = 0
    knowledge_retained_pct: float = 0.0

    memory_before: int = 0
    memory_after: int = 0
    memory_retained_pct: float = 0.0

    session_before: int = 0
    session_after: int = 0
    session_retained_pct: float = 0.0

    total_before: int = 0
    total_after: int = 0
    total_reduction_pct: float = 0.0

    question_tokens: int = 0
    question_trimmed: bool = False
    budget_latency_ms: float = 0.0
    total_context_tokens: int = 0
    total_prompt_tokens: int = 0
    within_budget: bool = False

    # Category caps verification
    knowledge_cap: int = 0
    memory_cap: int = 0
    session_cap: int = 0
    knowledge_at_or_below_cap: bool = False
    memory_at_or_below_cap: bool = False
    session_at_or_below_cap: bool = False

    pass_starvation_test: bool = False


def run_test_case(case: TestCase, budgeter: ContextBudgeter) -> EvaluationResult:
    """Run a single test case through the budgeter and capture metrics."""
    result = budgeter.build_context(
        question=case.question,
        knowledge_context=case.knowledge,
        memory_context=case.memory,
        conversation_summary=case.summary,
        recent_messages=case.recent,
    )
    m = result["metrics"]

    # Compute total prompt tokens (approximate: question + overhead + trimmed context)
    total_prompt = m.question_tokens + m.overhead_tokens + m.total_after
    available = m.total_budget - m.overhead_tokens - m.question_tokens

    # Verify caps
    knowledge_at_cap = m.knowledge_after <= m.knowledge_cap or m.knowledge_after == m.knowledge_before
    memory_at_cap = m.memory_after <= m.memory_cap or m.memory_after == m.memory_before
    session_at_cap = m.session_after <= m.session_cap or m.session_after == m.session_before

    # Starvation test: did any category get completely eliminated when it had content?
    starvation = False
    if m.knowledge_before > 0 and m.knowledge_after == 0:
        starvation = True
    if m.memory_before > 0 and m.memory_after == 0:
        starvation = True
    if m.session_before > 0 and m.session_after == 0:
        starvation = True

    return EvaluationResult(
        test_name=case.name,
        expected_behavior=case.expected_behavior,
        knowledge_before=m.knowledge_before,
        knowledge_after=m.knowledge_after,
        knowledge_retained_pct=round(m.knowledge_after / m.knowledge_before * 100, 2) if m.knowledge_before > 0 else 100.0,
        memory_before=m.memory_before,
        memory_after=m.memory_after,
        memory_retained_pct=round(m.memory_after / m.memory_before * 100, 2) if m.memory_before > 0 else 100.0,
        session_before=m.session_before,
        session_after=m.session_after,
        session_retained_pct=round(m.session_after / m.session_before * 100, 2) if m.session_before > 0 else 100.0,
        total_before=m.total_before,
        total_after=m.total_after,
        total_reduction_pct=m.reduction_percent(),
        question_tokens=m.question_tokens,
        question_trimmed=m.question_trimmed,
        budget_latency_ms=m.budget_latency_ms,
        total_context_tokens=m.total_after,
        total_prompt_tokens=total_prompt,
        within_budget=total_prompt <= m.total_budget,
        knowledge_cap=m.knowledge_cap,
        memory_cap=m.memory_cap,
        session_cap=m.session_cap,
        knowledge_at_or_below_cap=knowledge_at_cap,
        memory_at_or_below_cap=memory_at_cap,
        session_at_or_below_cap=session_at_cap,
        pass_starvation_test=not starvation,
    )


def run_evaluation() -> list[EvaluationResult]:
    """Run all test cases and return results."""
    budgeter = get_budgeter()
    print(f"Budgeter config: total={budgeter.total_budget}, overhead={budgeter.overhead_tokens}")
    print(f"Category caps: {budgeter.category_caps}")
    print()

    results = []
    for case in TEST_CASES:
        print(f"Running: {case.name} ...")
        result = run_test_case(case, budgeter)
        results.append(result)
        print(f"  Total: {result.total_before} -> {result.total_after} tokens "
              f"({result.total_reduction_pct}% reduction)")
        print(f"  Budget latency: {result.budget_latency_ms:.2f} ms")
        print(f"  Within budget: {result.within_budget}")
        print()

    return results


def generate_report(results: list[EvaluationResult]) -> str:
    """Generate a Markdown report from evaluation results."""

    # Aggregate statistics
    reduction_pcts = [r.total_reduction_pct for r in results if r.total_before > 0]
    budget_latencies = [r.budget_latency_ms for r in results]
    knowledge_retained = [r.knowledge_retained_pct for r in results if r.knowledge_before > 0]
    memory_retained = [r.memory_retained_pct for r in results if r.memory_before > 0]
    session_retained = [r.session_retained_pct for r in results if r.session_before > 0]
    within_budget_count = sum(1 for r in results if r.within_budget)
    starvation_pass_count = sum(1 for r in results if r.pass_starvation_test)

    report = []
    report.append("# Context Budgeting Evaluation Report")
    report.append("")
    report.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Budgeter Config:** total={results[0].total_prompt_tokens if results else 'N/A'}")
    report.append("")

    report.append("## Executive Summary")
    report.append("")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Test cases run | {len(results)} |")
    report.append(f"| Within budget | {within_budget_count}/{len(results)} ({round(within_budget_count/len(results)*100, 1)}%) |")
    report.append(f"| Starvation tests passed | {starvation_pass_count}/{len(results)} |")
    report.append(f"| Avg token reduction | {round(mean(reduction_pcts), 2)}% |")
    report.append(f"| Median token reduction | {round(median(reduction_pcts), 2)}% |")
    report.append(f"| Max token reduction | {round(max(reduction_pcts), 2)}% |")
    report.append(f"| Min token reduction | {round(min(reduction_pcts), 2)}% |")
    report.append(f"| Avg budget latency | {round(mean(budget_latencies), 3)} ms |")
    report.append(f"| Median budget latency | {round(median(budget_latencies), 3)} ms |")
    report.append("")

    report.append("## Context Retention by Category")
    report.append("")
    report.append(f"| Category | Avg Retained | Min Retained |")
    report.append(f"|----------|--------------|--------------|")
    report.append(f"| Knowledge | {round(mean(knowledge_retained), 2)}% | {round(min(knowledge_retained), 2)}% |")
    report.append(f"| Memory | {round(mean(memory_retained), 2)}% | {round(min(memory_retained), 2)}% |")
    report.append(f"| Session | {round(mean(session_retained), 2)}% | {round(min(session_retained), 2)}% |")
    report.append("")

    report.append("## Detailed Test Results")
    report.append("")
    for r in results:
        report.append(f"### {r.test_name}")
        report.append("")
        report.append(f"**Expected:** {r.expected_behavior}")
        report.append("")
        report.append(f"| Metric | Before | After | Retained |")
        report.append(f"|--------|--------|-------|----------|")
        report.append(f"| Knowledge | {r.knowledge_before} | {r.knowledge_after} | {r.knowledge_retained_pct}% |")
        report.append(f"| Memory | {r.memory_before} | {r.memory_after} | {r.memory_retained_pct}% |")
        report.append(f"| Session | {r.session_before} | {r.session_after} | {r.session_retained_pct}% |")
        report.append(f"| **Total** | **{r.total_before}** | **{r.total_after}** | **{r.total_reduction_pct}%** |")
        report.append("")
        report.append(f"- Question tokens: {r.question_tokens} (trimmed: {r.question_trimmed})")
        report.append(f"- Budget latency: {r.budget_latency_ms:.3f} ms")
        report.append(f"- Total prompt tokens: {r.total_prompt_tokens}")
        report.append(f"- Within budget: {r.within_budget}")
        report.append(f"- Caps respected: K={r.knowledge_at_or_below_cap}, M={r.memory_at_or_below_cap}, S={r.session_at_or_below_cap}")
        report.append(f"- Starvation test: {'PASS' if r.pass_starvation_test else 'FAIL'}")
        report.append("")

    report.append("## Key Findings")
    report.append("")

    if all(r.within_budget for r in results):
        report.append("1. **All prompts stay within budget.** The budgeter successfully enforces the token limit.")
    else:
        report.append(f"1. **{(len(results) - within_budget_count)} cases exceeded budget.** This may indicate question truncation or overhead underestimation.")

    if all(r.pass_starvation_test for r in results):
        report.append("2. **No category starvation.** Memory and session are never completely eliminated when they have content.")
    else:
        report.append("2. **Category starvation detected.** Lower-priority categories were completely removed in some cases.")

    avg_reduction = mean(reduction_pcts)
    if avg_reduction > 20:
        report.append(f"3. **Significant token reduction achieved.** Average reduction is {round(avg_reduction, 1)}%.")
    else:
        report.append(f"3. **Token reduction is modest ({round(avg_reduction, 1)}%).** This may indicate that most queries fit within budget naturally.")

    report.append("")
    report.append("## Recommendations")
    report.append("")
    report.append("1. **Monitor production logs** using `observability/metrics_logger.py` to confirm these synthetic results.")
    report.append("2. **Adjust category caps** if real usage shows one category is consistently more valuable.")
    report.append("3. **Consider dynamic budget sizing** based on query complexity once the intent engine is built.")
    report.append("4. **Investigate overhead estimation** if prompts still exceed budget in production.")
    report.append("")

    return "\n".join(report)


def main():
    print("=" * 60)
    print("CONTEXT BUDGETING EVALUATION")
    print("=" * 60)
    print()

    results = run_evaluation()

    report = generate_report(results)
    report_path = Path(__file__).resolve().parent / "report.md"
    report_path.write_text(report, encoding="utf-8")

    print()
    print("=" * 60)
    print(f"REPORT SAVED: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
