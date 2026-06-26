# Context Budgeting Evaluation Report

**Generated:** 2026-06-24 20:53:31
**Budgeter Config:** total=109

## Executive Summary

| Metric | Value |
|--------|-------|
| Test cases run | 10 |
| Within budget | 7/10 (70.0%) |
| Starvation tests passed | 10/10 |
| Avg token reduction | 5.72% |
| Median token reduction | 0.0% |
| Max token reduction | 39.74% |
| Min token reduction | 0.0% |
| Avg budget latency | 1203.512 ms |
| Median budget latency | 7.46 ms |

## Context Retention by Category

| Category | Avg Retained | Min Retained |
|----------|--------------|--------------|
| Knowledge | 93.12% | 56.87% |
| Memory | 100.0% | 100.0% |
| Session | 92.38% | 46.68% |

## Detailed Test Results

### small_all_fits

**Expected:** No trimming. All categories at 100%.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 18 | 18 | 100.0% |
| Memory | 10 | 10 | 100.0% |
| Session | 14 | 14 | 100.0% |
| **Total** | **42** | **42** | **0.0%** |

- Question tokens: 7 (trimmed: False)
- Budget latency: 11891.260 ms
- Total prompt tokens: 109
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### medium_all

**Expected:** Light trimming possible. Knowledge dominates.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 291 | 291 | 100.0% |
| Memory | 41 | 41 | 100.0% |
| Session | 63 | 63 | 100.0% |
| **Total** | **395** | **395** | **0.0%** |

- Question tokens: 11 (trimmed: False)
- Budget latency: 8.700 ms
- Total prompt tokens: 466
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### large_knowledge_starvation_test

**Expected:** Knowledge capped at 60%. Memory and session preserved at 25%/15%.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 2221 | 1957 | 88.11% |
| Memory | 10 | 10 | 100.0% |
| Session | 14 | 14 | 100.0% |
| **Total** | **2245** | **1981** | **11.76%** |

- Question tokens: 8 (trimmed: False)
- Budget latency: 40.810 ms
- Total prompt tokens: 2049
- Within budget: False
- Caps respected: K=False, M=True, S=True
- Starvation test: PASS

### large_memory_starvation_test

**Expected:** Memory capped at 25%. Knowledge gets 60%. Session gets 15%.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 18 | 18 | 100.0% |
| Memory | 406 | 406 | 100.0% |
| Session | 14 | 14 | 100.0% |
| **Total** | **438** | **438** | **0.0%** |

- Question tokens: 5 (trimmed: False)
- Budget latency: 4.640 ms
- Total prompt tokens: 503
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### large_session_starvation_test

**Expected:** Session capped at 15%. Knowledge gets 60%. Memory gets 25%.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 18 | 18 | 100.0% |
| Memory | 10 | 10 | 100.0% |
| Session | 632 | 632 | 100.0% |
| **Total** | **660** | **660** | **0.0%** |

- Question tokens: 5 (trimmed: False)
- Budget latency: 6.220 ms
- Total prompt tokens: 725
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### everything_large

**Expected:** All categories trimmed. Knowledge 60%, Memory 25%, Session 15%.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 2221 | 1263 | 56.87% |
| Memory | 406 | 406 | 100.0% |
| Session | 632 | 295 | 46.68% |
| **Total** | **3259** | **1964** | **39.74%** |

- Question tokens: 26 (trimmed: False)
- Budget latency: 41.520 ms
- Total prompt tokens: 2050
- Within budget: False
- Caps respected: K=False, M=True, S=False
- Starvation test: PASS

### query_overflow

**Expected:** Question truncated to 50% of budget. Context preserved.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 18 | 18 | 100.0% |
| Memory | 10 | 10 | 100.0% |
| Session | 14 | 14 | 100.0% |
| **Total** | **42** | **42** | **0.0%** |

- Question tokens: 3551 (trimmed: True)
- Budget latency: 38.640 ms
- Total prompt tokens: 3653
- Within budget: False
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### empty_context

**Expected:** Zero context. Fast path.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 0 | 0 | 100.0% |
| Memory | 0 | 0 | 100.0% |
| Session | 0 | 0 | 100.0% |
| **Total** | **0** | **0** | **0.0%** |

- Question tokens: 1 (trimmed: False)
- Budget latency: 0.070 ms
- Total prompt tokens: 61
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### knowledge_only

**Expected:** Knowledge gets full 60% + spare from memory/session. No trimming if fits.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 291 | 291 | 100.0% |
| Memory | 0 | 0 | 100.0% |
| Session | 0 | 0 | 100.0% |
| **Total** | **291** | **291** | **0.0%** |

- Question tokens: 4 (trimmed: False)
- Budget latency: 2.590 ms
- Total prompt tokens: 355
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

### memory_only

**Expected:** Memory gets full 25% + spare from knowledge/session. No trimming if fits.

| Metric | Before | After | Retained |
|--------|--------|-------|----------|
| Knowledge | 0 | 0 | 100.0% |
| Memory | 41 | 41 | 100.0% |
| Session | 0 | 0 | 100.0% |
| **Total** | **41** | **41** | **0.0%** |

- Question tokens: 5 (trimmed: False)
- Budget latency: 0.670 ms
- Total prompt tokens: 106
- Within budget: True
- Caps respected: K=True, M=True, S=True
- Starvation test: PASS

## Key Findings

1. **3 cases exceeded budget.** This may indicate question truncation or overhead underestimation.
2. **No category starvation.** Memory and session are never completely eliminated when they have content.
3. **Token reduction is modest (5.7%).** This may indicate that most queries fit within budget naturally.

## Recommendations

1. **Monitor production logs** using `observability/metrics_logger.py` to confirm these synthetic results.
2. **Adjust category caps** if real usage shows one category is consistently more valuable.
3. **Consider dynamic budget sizing** based on query complexity once the intent engine is built.
4. **Investigate overhead estimation** if prompts still exceed budget in production.
