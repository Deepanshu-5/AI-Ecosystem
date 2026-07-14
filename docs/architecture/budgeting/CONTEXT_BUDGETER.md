# Context Budgeting Architecture

## Part 1 --- Mission, Ownership, and Boundaries

### Mission

The Context Budgeting Layer transforms `RetrievedContext` into
deterministic, token-budget-compliant structured context for the Prompt
Builder.

``` text
Planner
  ↓
ExecutionPlan
  ↓
RetrieverIntegration
  ↓
RetrievedContext
  ↓
Context Budgeting Layer
  ↓
Budgeted Context
  ↓
Prompt Builder
```

### Owns

-   Context token allocation
-   Category budget allocation
-   Context item selection
-   Controlled truncation
-   Unused budget redistribution
-   Token accounting
-   Deterministic ordering
-   Budget diagnostics

### Does Not Own

-   Query analysis
-   Retrieval decisions
-   Knowledge, memory, or session retrieval
-   Vector search or reranking
-   Memory semantics
-   Session summarization
-   Prompt formatting
-   Model or tool selection
-   LLM generation

### Input Boundary

The layer consumes `RetrievedContext`.

It must not directly call:

-   `services.knowledge_service`
-   `memory.memory_service`
-   `memory.memory_retriever`
-   `conversation_memory`
-   `retrieval.retriever`
-   Integration Gateways
-   Integration Translators

The Budgeter is a consumer of the Retriever contract.

### Planner Boundary

The Budgeter must not reinterpret `ExecutionPlan` or request additional
resources.

Planner decides what resources are required. Retriever executes that
decision. The Budgeter only decides how much of the retrieved context
fits within the available token budget.

### Prompt Builder Boundary

The Budgeter returns structured context.

It must not:

-   Create prompt sections
-   Add system instructions
-   Add answer-style instructions
-   Format the final LLM prompt

These belong to the Prompt Builder.

### Architectural Invariant

> The Context Budgeting Layer may reduce, select, allocate, and account
> for retrieved context, but may never retrieve, reinterpret Planner
> decisions, or construct prompts.



# Context Budgeting Architecture

## Part 2 --- Input and Output Contracts

### Input Contract

The Context Budgeting Layer accepts:

-   `RetrievedContext`
-   Query
-   Total token budget
-   Reserved token budget

`RetrievedContext` is the canonical context input.

The Budgeter consumes the existing:

-   `KnowledgeContext`
-   `MemoryContext`
-   `SessionContext`

### ContextItem Decision

Do not introduce `ContextItem` as the new cross-layer contract.

The existing Retriever domain already defines:

-   `KnowledgeItem`
-   `MemoryEntry`
-   `SessionMessage`

Creating another generic context model would duplicate existing domain
contracts.

### Query Input

The query is used only for token accounting.

The Budgeter may:

-   Count query tokens
-   Apply the explicit query overflow policy

The Budgeter must not:

-   Analyze query intent
-   Classify complexity
-   Change Planner decisions

### Budget Input

The Budgeter receives:

-   `total_budget`
-   `reserved_budget`

Available context budget is:

``` text
context_budget = total_budget - reserved_budget - query_tokens
```

The Budgeter must never allocate more than the available context budget.

### Output Contract

Introduce an immutable `BudgetedContext`.

``` text
BudgetedContext
├── knowledge
├── memory
├── session
├── metadata
└── version
```

`BudgetedContext` represents retrieved context after token budgeting.

It remains structured and must not contain final prompt formatting.

### Budget Metadata

Introduce immutable `BudgetMetadata`.

Minimum fields:

``` text
total_budget
reserved_tokens
query_tokens
context_budget
used_context_tokens
remaining_tokens
knowledge_tokens
memory_tokens
session_tokens
```

Metadata records budgeting facts only.

It must not contain Planner, Router, provider, model, or cost decisions.

### Immutability

`BudgetedContext` and `BudgetMetadata` are immutable contracts.

The Budgeter must not mutate `RetrievedContext`.

### Architectural Invariants

> `RetrievedContext` is the canonical budgeting input.

> `ContextItem` is not the cross-layer budgeting contract.

> Budgeting produces structured `BudgetedContext`, not prompt text.

> `RetrievedContext` must never be mutated.

> Budget metadata records allocation facts only.

## Part 3 --- Budgetable Unit Model

### Core Decision

Do not create a generic `ContextItem`.

The Budgeter works directly with the existing Retriever domain objects:

-   `KnowledgeItem`
-   `MemoryEntry`
-   `SessionMessage`
-   Session summary text

Each object is treated as an independent budgetable unit.

### Knowledge Units

Each `KnowledgeItem` is one budgetable unit.

Token count is calculated from:

``` text
KnowledgeItem.text
```

Selection preserves the order received from `RetrievedContext`.

The Budgeter does not rerank knowledge items or reinterpret their score.

### Memory Units

Each `MemoryEntry` is one budgetable unit.

Token count is calculated from:

``` text
MemoryEntry.content
```

Selection preserves the order received from `RetrievedContext`.

The Budgeter does not convert distance, similarity, or score semantics.

### Session Units

Session context contains two unit types:

``` text
Session summary
Recent SessionMessage objects
```

The session summary is one budgetable unit when it is not empty.

Each `SessionMessage` is one separate budgetable unit.

Token count for a message is calculated from:

``` text
SessionMessage.content
```

The Budgeter does not summarize or merge session messages.

### Selection Rule

Units are evaluated in their existing order.

For each category:

``` text
First unit
  ↓
Count tokens
  ↓
Fits available category budget?
  ├── Yes → Select
  └── No  → Apply truncation policy defined later
```

The Budgeter must not reorder units using score, length, or custom
priority logic.

Retrieval and ranking ownership remains upstream.

### Internal Token Accounting

Token counts may be calculated internally during budgeting.

Token counts do not need to be added to:

-   `KnowledgeItem`
-   `MemoryEntry`
-   `SessionMessage`

This avoids modifying Retriever domain contracts for Budgeter-specific
concerns.

### No Generic Wrapper

Do not introduce objects such as:

``` text
ContextItem
BudgetableItem
RankedContextItem
TokenizedContextItem
```

The Budgeter may use private local variables or private helper logic for
token accounting, but no new public generic context contract is
required.

### Architectural Invariants

> Existing Retriever domain objects are the budgeting units.

> The Budgeter preserves upstream ordering.

> The Budgeter does not rerank or reinterpret scores.

> Session summary and session messages are budgeted separately.

> Token accounting remains Budgeter-owned and does not modify Retriever
> contracts.


## Part 4 --- Token Budget Model and Reservation

### Budget Inputs

The Budgeter receives:

``` text
total_budget
reserved_budget
query
RetrievedContext
```

`total_budget` is the maximum token budget available for the complete
downstream prompt boundary.

`reserved_budget` protects tokens required by the future Prompt Builder
for system instructions, formatting, and other fixed prompt overhead.

### Query Accounting

The query is counted before context allocation.

``` text
query_tokens = count(query)
```

The query is not part of the context category budgets.

### Context Budget Calculation

Available context budget is calculated once:

``` text
context_budget =
    total_budget
    - reserved_budget
    - query_tokens
```

The Budgeter must never increase this value using minimum-budget
fallbacks.

If the calculated context budget is negative, overflow policy applies.

### Category Budgets

The context budget is divided between:

``` text
Knowledge
Memory
Session
```

Initial category caps remain:

``` text
Knowledge = 60%
Memory    = 25%
Session   = 15%
```

Category budgets are calculated from `context_budget`, not
`total_budget`.

Example:

``` text
context_budget = 1000

Knowledge = 600
Memory    = 250
Session   = 150
```

### Category Caps

Category percentages define initial allocation limits.

They are not permanent unused reservations.

If one category does not use its allocation, unused tokens may be
redistributed to other categories.

Redistribution rules are defined in a later part.

### Hard Budget Invariant

The final accounting must satisfy:

``` text
reserved_tokens
+ query_tokens
+ used_context_tokens
<= total_budget
```

No truncation marker, separator, metadata value, or internal fallback
may cause the final accounted token total to exceed `total_budget`.

### Token Counter Ownership

The Budgeter uses the shared token-counting capability.

The Budgeter owns when token counting occurs.

The token counter owns how text tokens are counted and truncated.

The Budgeter must not implement its own character-based token
estimation.

### Configuration

Default values may come from project settings.

Explicit constructor or method inputs may override defaults for testing
and controlled execution.

The Budgeter must not silently replace invalid configuration with
fallback values.

Invalid budgets must fail validation.

### Architectural Invariants

> Context budget is derived from the real remaining total budget.

> Query tokens are reserved before context allocation.

> Category percentages apply only to the available context budget.

> Unused category allocation may be redistributed.

> Final accounted token usage must never exceed `total_budget`.

> Invalid budget configuration must not be silently repaired.

## Part 5 --- Priority and Allocation Algorithm

### Core Decision

Use a deterministic two-phase allocation algorithm.

The Budgeter preserves category priority:

``` text
Knowledge
Memory
Session
```

This order is used for allocation and redistribution.

The Budgeter does not calculate new relevance scores or rerank retrieved
units.

### Phase 1 --- Category Allocation

Each category receives its initial budget:

``` text
Knowledge = 60% of context_budget
Memory    = 25% of context_budget
Session   = 15% of context_budget
```

Within each category, units are evaluated in the order received from
`RetrievedContext`.

A unit is selected when it fits within the remaining category budget.

If a unit does not fit, the truncation policy defined later applies.

Phase 1 records:

``` text
selected units
used tokens
unused category tokens
unselected units
```

### Phase 2 --- Unused Budget Redistribution

After Phase 1, all unused category tokens form a shared redistribution
pool.

``` text
redistribution_pool =
    context_budget
    - phase_1_used_tokens
```

Remaining units are reconsidered in fixed order:

``` text
Knowledge
Memory
Session
```

Within each category, original retrieval order is preserved.

Units selected in Phase 1 must not be selected again.

### Session Ordering

Within the Session category, allocation order is:

``` text
Session summary
Recent messages in existing order
```

The Budgeter must not reorder recent messages.

### No Score-Based Priority

The Budgeter must not sort using:

``` text
KnowledgeItem.score
MemoryEntry.score
text length
token count
custom priority values
```

Ranking belongs upstream.

The Budgeter only performs budget allocation over the order already
provided by Retriever.

### Stop Condition

Allocation stops when:

-   No remaining unit can be selected under the applicable truncation
    policy, or
-   The context budget is fully consumed.

The Budgeter must not exceed `context_budget` to include one additional
unit.

### Determinism

For identical:

``` text
RetrievedContext
query
total_budget
reserved_budget
token counter behavior
```

the selected context and token accounting must be identical.

Timing values are not part of budgeting selection logic.

### Architectural Invariants

> Allocation uses a deterministic two-phase algorithm.

> Initial category allocation follows the configured category caps.

> Unused tokens become a shared redistribution pool.

> Redistribution order is Knowledge → Memory → Session.

> Original order inside each category is preserved.

> The Budgeter never reranks retrieved context.

> No unit may be selected twice.

> Allocation must never exceed the available context budget.

## Part 6 --- Category Caps and Redistribution Rules

### Initial Category Caps

Default context allocation is:

``` text
Knowledge = 60%
Memory    = 25%
Session   = 15%
```

The percentages must total `100%`.

Category caps apply only during Phase 1.

They prevent one category from consuming the full context budget before
other categories receive an initial allocation opportunity.

### Cap Calculation

Category budgets are derived from `context_budget`.

Integer token budgets must be calculated deterministically.

Any rounding remainder stays unallocated and becomes part of the Phase 2
redistribution pool.

The Budgeter must not exceed `context_budget` because of percentage
rounding.

### Unused Allocation

A category may use less than its Phase 1 allocation because:

-   It has no context units
-   Its available units do not fit
-   Its units consume less than the category budget

Unused tokens are not permanently reserved.

They move into the shared redistribution pool.

### Redistribution

Phase 2 uses the remaining real context budget:

``` text
remaining_budget =
    context_budget
    - used_context_tokens
```

Remaining units are reconsidered in this fixed category order:

``` text
Knowledge
Memory
Session
```

Original order inside each category is preserved.

Phase 1 category caps do not apply during redistribution.

The only hard limit in Phase 2 is the remaining context budget.

### Empty Categories

An empty category consumes zero tokens.

Its full initial allocation becomes available for redistribution.

The Budgeter must not create placeholder context for an empty category.

### Configurable Caps

Category caps may come from configuration.

Valid caps must:

-   Be numeric
-   Be non-negative
-   Total exactly `1.0`

Invalid cap configuration must fail validation.

The Budgeter must not silently normalize or replace invalid percentages.

### Architectural Invariants

> Category caps protect initial allocation fairness.

> Category caps apply only during Phase 1.

> Unused category tokens are redistributable.

> Phase 2 is limited by the real remaining context budget.

> Empty categories consume no budget.

> Percentage rounding must never cause budget overflow.

> Invalid category caps must fail validation.


 ## Part 7 --- Truncation and Overflow Semantics

### Core Rule

Truncation is a controlled fallback.

The Budgeter first attempts to select complete units.

A unit is truncated only when it does not fit and the remaining
applicable budget is greater than zero.

### Unit Truncation

Only textual content may be truncated:

``` text
KnowledgeItem.text
MemoryEntry.content
Session summary
SessionMessage.content
```

The Budgeter must preserve the original domain identity and metadata of
the selected unit.

The original `RetrievedContext` and its objects must not be mutated.

### Truncation Limit

Truncated text must fit inside the exact remaining token allocation.

Any truncation marker must be included in the token limit.

The final token count of the truncated text must satisfy:

``` text
truncated_tokens <= remaining_budget
```

The Budgeter must not truncate to the limit and then append extra text
that causes overflow.

### Zero Remaining Budget

If the remaining applicable budget is zero, the unit is not selected.

Empty truncated units must not be created.

### Query Overflow

The query is preserved by default.

If:

``` text
query_tokens + reserved_budget > total_budget
```

the Budgeter may truncate the query to the exact available query budget:

``` text
query_budget = total_budget - reserved_budget
```

If `query_budget <= 0`, budgeting fails validation.

The Budgeter must record whether query truncation occurred.

The downstream Prompt Builder must receive the effective query used for
budgeting.

### Context Overflow

Context overflow is handled through:

``` text
selection
truncation
omission
```

It must not raise an error merely because all retrieved context cannot
fit.

The Budgeter returns the best deterministic selection allowed by the
allocation algorithm.

### Truncated Unit Handling

After a unit is truncated and selected:

-   It is considered consumed
-   It must not be reconsidered in Phase 2
-   The remaining original text is not emitted as another unit

This prevents duplicate or fragmented context.

### Metadata

Budget metadata must additionally record:

``` text
query_truncated
truncated_unit_count
```

These are budgeting facts and are useful for validation and
observability.

### Architectural Invariants

> Complete units are preferred before truncation.

> Truncated content must fit the exact remaining token budget.

> Truncation markers are included in token accounting.

> RetrievedContext is never mutated.

> Query overflow uses an explicit truncation policy.

> Context overflow is handled by selection, truncation, and omission.

> A truncated unit is selected at most once.

## Part 8 --- Determinism and Ordering

### Determinism

For identical inputs and identical token-counter behavior, the Budgeter
must produce identical:

-   Effective query
-   Selected context
-   Truncated content
-   Token accounting
-   Metadata

Timing and runtime measurements must not affect selection.

### Category Order

The fixed category order is:

``` text
Knowledge
Memory
Session
```

This order applies to Phase 1 and Phase 2.

### Unit Order

The Budgeter preserves the order received from `RetrievedContext`.

Within Session:

``` text
Session summary
Recent messages in existing order
```

The Budgeter must not sort by score, length, token count, or metadata.

### Stable Serialization

`BudgetedContext.to_dict()` and `BudgetMetadata.to_dict()` must use a
stable field structure.

Serialization must not depend on unordered runtime state.

### Architectural Invariants

> Identical inputs produce identical budgeting results.

> Upstream retrieval order is preserved.

> Timing does not influence selection.

> Serialization structure is stable.


## Part 9 --- Validation and Exception Model

### Validation Ownership

The Context Budgeting Layer validates its own inputs and output.

It does not replace Retriever validation.

### Input Validation

Reject:

-   Non-`RetrievedContext` input
-   Non-string query
-   Empty query
-   Non-positive `total_budget`
-   Negative `reserved_budget`
-   `reserved_budget >= total_budget`
-   Invalid category caps

Invalid inputs must not be silently repaired.

### Output Validation

Before returning, validate:

``` text
used_context_tokens <= context_budget
reserved_tokens + query_tokens + used_context_tokens <= total_budget
remaining_tokens >= 0
category token counts >= 0
sum(category token counts) == used_context_tokens
```

Selected output must contain only valid budgeting domain objects.

### Exception Model

Introduce:

``` text
ContextBudgetingError
ContextBudgetValidationError
ContextBudgetOverflowError
```

`ContextBudgetingError` is the base budgeting exception.

`ContextBudgetValidationError` represents invalid input, configuration,
or output state.

`ContextBudgetOverflowError` is reserved for a budget state that cannot
be satisfied under the explicit overflow policy.

Normal context omission because retrieved content does not fit is not an
error.

### Failure Behavior

The Budgeter must fail explicitly.

It must not:

-   Silently replace invalid configuration
-   Increase the available budget
-   Return over-budget output
-   Catch broad exceptions and return default budgeting results

### Architectural Invariants

> Budgeting validation is owned by the Budgeting Layer.

> Invalid state fails explicitly.

> Normal context omission is not an exception.

> Over-budget output must never be returned.

> Budgeting exceptions remain specific to the Budgeting Layer.

## Part 10 --- Integration Boundary

### Pipeline Position

The Context Budgeting Layer sits between Retriever and Prompt Builder.

``` text
ExecutionPlan
  ↓
RetrieverIntegration
  ↓
RetrievedContext
  ↓
ContextBudgeter
  ↓
BudgetedContext
  ↓
Prompt Builder
```

### Retriever Boundary

The Budgeter accepts `RetrievedContext`.

It must not:

-   Call Retriever components
-   Call Integration components
-   Call Gateways or Translators
-   Perform retrieval
-   Modify `RetrievedContext`

Retriever owns context acquisition.

The Budgeter owns context reduction and token allocation.

### Planner Boundary

The Budgeter does not require `ExecutionPlan` for V1.

Planner decisions have already been executed by Retriever.

The Budgeter must not reinterpret resource requirements or request
missing context.

### Prompt Builder Boundary

The Prompt Builder consumes:

``` text
BudgetedContext
effective_query
```

The Budgeter returns structured context.

It must not:

-   Build prompt sections
-   Add system instructions
-   Add answer constraints
-   Produce the final prompt string

### Query Handoff

If the query is not truncated:

``` text
effective_query = original query
```

If query overflow policy truncates the query:

``` text
effective_query = truncated query
```

The effective query used for token accounting must be the same query
passed downstream to the Prompt Builder.

### Legacy Boundary

The new budgeting path must not depend on:

``` text
ContextItem
retrieval.retriever
services.knowledge_service
memory.memory_service
conversation_memory
llm.rag
```

Legacy callers may remain temporarily during migration, but they must
not define the new Budgeting Layer contract.

### Architectural Invariants

> `RetrievedContext` is the only retrieved-context input boundary.

> The Budgeter does not consume or reinterpret `ExecutionPlan` in V1.

> `BudgetedContext` is the structured output boundary.

> The effective query used for accounting is passed unchanged to the
> Prompt Builder.

> Prompt construction remains outside the Budgeting Layer.

> Legacy orchestration paths do not define the new budgeting contract.

## Part 11 --- Package and File Architecture

### Core Decision

Create a dedicated top-level package:

``` text
budgeting/
```

The new Context Budgeting Layer must not remain inside
`services/context_budgeter.py`.

`services/` is infrastructure-oriented and already contains legacy
budgeting logic. The new Budgeter is a first-class architectural layer
between Retriever and Prompt Builder.

### Package Structure

``` text
budgeting/
├── __init__.py
├── budgeted_context.py
├── budget_metadata.py
├── context_budgeter.py
├── budget_validator.py
└── exceptions.py
```

### File Responsibilities

#### `budgeted_context.py`

Owns the immutable `BudgetedContext` output contract.

Contains no budgeting algorithm or infrastructure calls.

#### `budget_metadata.py`

Owns immutable `BudgetMetadata`.

Contains token allocation and truncation facts only.

#### `context_budgeter.py`

Owns budgeting orchestration:

``` text
validate input
  ↓
count query tokens
  ↓
calculate context budget
  ↓
calculate category budgets
  ↓
Phase 1 allocation
  ↓
Phase 2 redistribution
  ↓
build BudgetedContext
  ↓
validate output
```

Private helper methods may be used for internal allocation and
truncation logic.

#### `budget_validator.py`

Owns Budgeting Layer validation.

Validates:

-   Budget inputs
-   Category caps
-   `BudgetedContext`
-   Token accounting invariants

It must not perform allocation.

#### `exceptions.py`

Owns:

``` text
ContextBudgetingError
ContextBudgetValidationError
ContextBudgetOverflowError
```

#### `__init__.py`

Exposes the public Budgeting Layer API.

Minimum public API:

``` text
ContextBudgeter
BudgetedContext
BudgetMetadata
ContextBudgetingError
ContextBudgetValidationError
ContextBudgetOverflowError
```

### Dependency Direction

Allowed:

``` text
budgeting
  ↓
retriever
shared.token_counter
```

The Budgeting Layer may also read validated default configuration.

Not allowed:

``` text
budgeting → planner
budgeting → integration
budgeting → retrieval
budgeting → memory
budgeting → conversation_memory
budgeting → llm
budgeting → services.knowledge_service
```

### Legacy File

Existing:

``` text
services/context_budgeter.py
```

is legacy.

Do not use it as the foundation of the new package.

Do not delete it during initial implementation because existing legacy
callers still depend on it.

Migration and removal are handled separately.

### Architectural Invariants

> Budgeting is a dedicated architectural layer.

> Domain contracts, validation, exceptions, and orchestration have
> explicit ownership.

> `context_budgeter.py` owns allocation, not every budgeting concern.

> The new package depends on Retriever contracts and token-counting
> capability only.

> Legacy `services/context_budgeter.py` remains isolated during initial
> migration.
## Part 12 — Testing and Acceptance Criteria

### Test Structure

Create:

```text
tests/budgeting/
├── test_budgeted_context.py
├── test_budget_metadata.py
├── test_context_budgeter.py
└── test_budget_validator.py
```

### Contract Tests

Verify:

* `BudgetedContext` creation
* `BudgetMetadata` creation
* Immutability
* Stable serialization
* Default schema version
* Empty structured context
* Correct nested context types

### Budgeter Tests

Verify:

* Empty `RetrievedContext`
* Knowledge-only context
* Memory-only context
* Session-only context
* All context categories
* Initial category caps
* Category allocation from `context_budget`
* Unused budget redistribution
* Empty-category redistribution
* Deterministic category order
* Original unit order preservation
* Query token accounting
* Query truncation
* Unit truncation
* Truncation marker accounting
* Zero remaining budget
* Context omission when no budget remains
* No duplicate unit selection
* Session summary before recent messages
* Truncated units are not reconsidered
* Original `RetrievedContext` is not mutated
* Deterministic output

### Validator Tests

Verify rejection of:

* Non-`RetrievedContext` input
* Non-string query
* Empty query
* Non-positive `total_budget`
* Negative `reserved_budget`
* `reserved_budget >= total_budget`
* Non-numeric category caps
* Negative category caps
* Category caps that do not total `1.0`
* Negative token metadata
* Category token count mismatch
* `used_context_tokens > context_budget`
* Total accounted token usage greater than `total_budget`
* Negative remaining token count
* Invalid `BudgetedContext`
* Invalid `BudgetMetadata`

### Allocation Invariant Tests

Verify:

```text
used_context_tokens <= context_budget
```

Verify:

```text
reserved_tokens
+ query_tokens
+ used_context_tokens
<= total_budget
```

Verify:

```text
knowledge_tokens
+ memory_tokens
+ session_tokens
== used_context_tokens
```

Verify:

```text
remaining_tokens >= 0
```

Verify that no selected context unit appears more than once.

Verify that category percentage rounding never causes allocation beyond `context_budget`.

### Determinism Tests

For identical:

```text
RetrievedContext
query
total_budget
reserved_budget
category caps
token-counter behavior
```

verify identical:

```text
effective query
selected knowledge
selected memory
selected session context
truncated content
token accounting
budget metadata
serialized output
```

Runtime timing must not affect selection.

### Regression Tests

After implementation, run:

```text
python -m pytest tests/budgeting -v
python -m pytest tests/integration -v
python -m pytest tests/retriever -v
python -m pytest tests/planner -v
python -m pytest
```

Existing Planner, Retriever, and Integration tests must continue to pass.

The current validated baseline is:

```text
Planner     = 52 tests
Retriever   = 84 tests
Integration = 48 tests

Existing baseline = 184 passing tests
```

No regression is allowed.

### Acceptance Criteria

The Context Budgeting Layer is accepted only when:

* `RetrievedContext` is the canonical context input
* The original query is accepted for token accounting
* `BudgetedContext` is the structured output
* `BudgetMetadata` records budgeting facts
* No retrieval occurs inside Budgeting
* No prompt formatting occurs inside Budgeting
* No `ExecutionPlan` reinterpretation occurs
* No generic `ContextItem` contract is introduced
* Existing Retriever domain objects are used as budgeting units
* Context allocation never exceeds `context_budget`
* Total accounted usage never exceeds `total_budget`
* Query overflow follows the explicit query truncation policy
* Unit truncation includes truncation markers in token accounting
* Upstream context ordering is preserved
* Session summary is considered before recent session messages
* No context unit is selected twice
* `RetrievedContext` is never mutated
* Allocation is deterministic
* Invalid state fails explicitly
* Invalid configuration is not silently repaired
* Existing project tests have no regressions

## Part 13 — Legacy Migration and Compatibility

### Legacy Budgeter

The existing file:

```text
services/context_budgeter.py
```

remains temporarily unchanged.

It supports current legacy consumers, including:

```text
llm/rag.py
mcp_server/tools/search_knowledge.py
evaluation/evaluate_budgeting.py
evaluation/quality_comparison.py
```

The new `budgeting/` package must not depend on the legacy Budgeter.

### No Immediate Deletion

Do not delete, rewrite, or migrate the legacy Budgeter during the initial Context Budgeting Layer implementation.

Doing so would combine two architectural changes:

```text
New Budgeting Layer implementation
+
Legacy control-flow migration
```

These changes must remain separate and independently testable.

### New Architecture Path

The new architecture is:

```text
Query
  ↓
Planner
  ↓
ExecutionPlan
  ↓
RetrieverIntegration
  ↓
RetrievedContext
  ↓
budgeting.ContextBudgeter
  ↓
BudgetedContext
  ↓
Future Prompt Builder
```

This is the canonical new control path.

### Temporary Legacy Path

The existing legacy paths may temporarily remain:

```text
llm/rag.py
  ↓
knowledge_service
memory_service
session_memory
  ↓
services.context_budgeter
```

and:

```text
mcp_server/tools/search_knowledge.py
  ↓
knowledge_service
memory_service
session_memory
  ↓
services.context_budgeter
```

These paths are transitional.

They must not define the new Budgeting Layer architecture.

### ContextItem Isolation

The existing:

```text
ContextItem
```

belongs only to the legacy Budgeter.

It may temporarily remain inside:

```text
services/context_budgeter.py
```

It must not be imported into:

```text
budgeting/
retriever/
integration/
planner/
```

No new production code should adopt `ContextItem`.

### Legacy API Isolation

The following APIs remain legacy:

```text
get_budgeter()
build_context()
build_context_from_items()
ContextItem
```

The new Budgeting Layer does not need API compatibility with these interfaces.

The new Budgeter contract is based on:

```text
RetrievedContext
  ↓
ContextBudgeter
  ↓
BudgetedContext
```

### Implementation Boundary

Initial implementation may create:

```text
budgeting/
├── __init__.py
├── budgeted_context.py
├── budget_metadata.py
├── context_budgeter.py
├── budget_validator.py
└── exceptions.py
```

and:

```text
tests/budgeting/
```

Initial implementation must not modify legacy consumers merely to use the new Budgeter.

Specifically, do not wire the new Budgeter into:

```text
llm/rag.py
mcp_server/server.py
mcp_server/tools/search_knowledge.py
retrieval/query.py
main.py
```

during this implementation phase.

### Migration Sequence

After the new Context Budgeting Layer is implemented and validated:

```text
1. Design the new Prompt Builder contract
2. Implement the new Prompt Builder
3. Connect BudgetedContext to the Prompt Builder
4. Design the new application control flow
5. Wire Planner → RetrieverIntegration → ContextBudgeter → Prompt Builder
6. Validate the complete new pipeline
7. Migrate the local RAG entry point
8. Migrate the MCP entry point
9. Trace all legacy Budgeter consumers
10. Remove dead legacy consumers
11. Remove services/context_budgeter.py only when no live consumer remains
```

### Removal Rule

The legacy Budgeter may be removed only when:

* No production file imports it
* No test depends on it
* No evaluation script requires it
* MCP uses the new control flow
* Local RAG uses the new control flow
* Full project tests pass after removal

Deletion must be based on verified dependency tracing.

### Compatibility Rule

The new Budgeting Layer is not required to preserve behavior from the legacy Budgeter when that behavior conflicts with the frozen architecture.

Examples include:

```text
MIN_CONTEXT_BUDGET fallback
parallel ContextItem architecture
silent invalid-configuration fallback
legacy string-based context assembly
legacy migration assumptions
```

The frozen Context Budgeting architecture takes precedence for the new package.

### Architectural Invariants

> New Budgeting architecture and legacy migration are separate changes.

> Legacy callers remain operational during initial implementation.

> `ContextItem` remains isolated to legacy code.

> No new architectural layer depends on `services/context_budgeter.py`.

> The new Budgeter is based on `RetrievedContext`.

> Legacy APIs do not constrain the new Budgeter contract.

> Legacy deletion occurs only after consumer migration and dependency tracing are verified.

## Part 14 — Architecture Freeze and Implementation Rules

### Architecture Freeze

Parts 1 through 13 define the frozen V1 Context Budgeting architecture.

The implementation must follow these decisions without introducing alternative contracts, allocation models, or cross-layer dependencies.

The canonical flow is:

```text
Query
  ↓
Planner
  ↓
ExecutionPlan
  ↓
RetrieverIntegration
  ↓
RetrievedContext
  ↓
ContextBudgeter
  ↓
BudgetedContext
  ↓
Future Prompt Builder
```

### Canonical Contracts

The Budgeting Layer accepts:

```text
RetrievedContext
query
total_budget
reserved_budget
```

The Budgeting Layer returns:

```text
BudgetedContext
```

`BudgetedContext` contains:

```text
knowledge
memory
session
metadata
version
```

`BudgetMetadata` records:

```text
total_budget
reserved_tokens
query_tokens
context_budget
used_context_tokens
remaining_tokens
knowledge_tokens
memory_tokens
session_tokens
query_truncated
truncated_unit_count
```

The effective query used for token accounting must be available to the downstream Prompt Builder.

### Required Package

Implement:

```text
budgeting/
├── __init__.py
├── budgeted_context.py
├── budget_metadata.py
├── context_budgeter.py
├── budget_validator.py
└── exceptions.py
```

Create:

```text
tests/budgeting/
├── test_budgeted_context.py
├── test_budget_metadata.py
├── test_context_budgeter.py
└── test_budget_validator.py
```
Implement the V1 Context Budgeting Layer defined in `CONTEXT_BUDGETING.md`.

Treat `CONTEXT_BUDGETING.md` as the authoritative implementation contract for this task.

Also preserve the existing project architecture and engineering rules defined in the provided project documents.

Requirements:

* Implement the architecture exactly as frozen in Parts 1–14.
* Trace existing contracts and dependencies before writing code.
* Reuse the existing Retriever domain contracts exactly as defined.
* Do not redesign the budgeting architecture.
* Do not introduce `ContextItem` or another generic context wrapper.
* Do not modify Planner, Retriever, or Integration contracts.
* Do not migrate or rewrite legacy callers.
* Do not modify `services/context_budgeter.py`.
* Do not wire the new Budgeter into `main.py`, `llm/rag.py`, MCP, or `retrieval/query.py`.
* Create the `budgeting/` package and `tests/budgeting/` tests defined by the document.
* Implement validation, deterministic two-phase allocation, redistribution, query overflow, and controlled truncation exactly as specified.
* Preserve the existing 184-test validated baseline.
* Do not make unrelated cleanup or refactoring changes.

Before implementation, inspect the existing source files required by the new layer, especially the Retriever contracts and `shared/token_counter.py`.

After implementation, run all required tests from Part 14.

Then provide the exact Implementation Completion Report required by Part 14, including every new file, every modified file, test counts, full-suite result, and any deviation from the architecture.

If the document contains an actual implementation ambiguity or contradiction, stop and report the exact section and conflict before making an architectural assumption.

### Implementation Rules

The implementation must:

* Consume `RetrievedContext`
* Preserve Retriever domain objects where content is unchanged
* Create new domain objects when textual content is truncated
* Never mutate `RetrievedContext`
* Preserve upstream category ordering
* Preserve unit ordering inside each category
* Treat session summary before recent session messages
* Use the deterministic two-phase allocation algorithm
* Apply category caps only during Phase 1
* Redistribute unused budget during Phase 2
* Count the query before context allocation
* Enforce the real remaining context budget
* Include truncation markers in token accounting
* Prevent duplicate unit selection
* Validate inputs before allocation
* Validate output before return
* Fail explicitly on invalid configuration or impossible budget state
* Produce stable serialization

### Forbidden Implementation Decisions

Do not:

* Introduce `ContextItem`
* Introduce another generic context wrapper
* Modify Retriever domain contracts
* Modify Planner contracts
* Consume `ExecutionPlan`
* Perform retrieval
* Call Integration Gateways
* Call Integration Translators
* Call knowledge, memory, or session infrastructure
* Rerank retrieved context
* Reinterpret scores
* Sort by token count or text length
* Build prompt strings
* Add system instructions
* Add answer-style constraints
* Silently normalize invalid category caps
* Silently replace invalid budgets
* Increase context budget using a minimum-budget fallback
* Return over-budget output
* Modify legacy callers during initial implementation

### Allocation Rules

Phase 1 uses:

```text
Knowledge = 60%
Memory    = 25%
Session   = 15%
```

unless valid configured caps are explicitly supplied.

Within each category, units are processed in existing Retriever order.

Phase 2 creates a shared redistribution pool from the real remaining context budget.

Redistribution order is:

```text
Knowledge
Memory
Session
```

Phase 1 category caps do not apply during Phase 2.

No unit may be selected more than once.

### Truncation Rules

Complete units are preferred.

If a unit does not fit and the applicable remaining budget is greater than zero, controlled truncation may be used.

Only textual content may be truncated.

Truncation applies to:

```text
KnowledgeItem.text
MemoryEntry.content
Session summary
SessionMessage.content
```

The truncated content, including any truncation marker, must fit inside the exact remaining token allocation.

A truncated unit is considered consumed and must not be reconsidered.

The original Retriever object must remain unchanged.

### Query Overflow Rules

The query is preserved by default.

If:

```text
query_tokens + reserved_budget > total_budget
```

calculate:

```text
query_budget = total_budget - reserved_budget
```

If:

```text
query_budget <= 0
```

raise a Budgeting Layer validation or overflow exception.

Otherwise, truncate the query to the exact query budget.

The truncated query becomes the effective query.

The effective query used for accounting must be the query passed downstream.

### Validation Rules

Input validation must reject:

* Non-`RetrievedContext` input
* Non-string query
* Empty query
* Non-positive `total_budget`
* Negative `reserved_budget`
* `reserved_budget >= total_budget`
* Non-numeric category caps
* Negative category caps
* Category caps that do not total `1.0`

Output validation must enforce:

```text
used_context_tokens <= context_budget
```

```text
reserved_tokens
+ query_tokens
+ used_context_tokens
<= total_budget
```

```text
knowledge_tokens
+ memory_tokens
+ session_tokens
== used_context_tokens
```

```text
remaining_tokens >= 0
```

Over-budget output must never be returned.

### Exception Rules

Implement:

```text
ContextBudgetingError
ContextBudgetValidationError
ContextBudgetOverflowError
```

`ContextBudgetingError` is the base exception.

`ContextBudgetValidationError` represents invalid input, configuration, or output state.

`ContextBudgetOverflowError` represents a budget state that cannot be satisfied under the explicit overflow policy.

Normal omission of context because it does not fit is not an exception.

### Dependency Rules

Allowed:

```text
budgeting
  ↓
retriever
shared.token_counter
validated configuration
```

Forbidden:

```text
budgeting → planner
budgeting → integration
budgeting → retrieval
budgeting → memory
budgeting → conversation_memory
budgeting → llm
budgeting → services.context_budgeter
budgeting → services.knowledge_service
```

### Legacy Protection

Do not delete or rewrite:

```text
services/context_budgeter.py
```

during initial implementation.

Do not migrate:

```text
llm/rag.py
mcp_server/server.py
mcp_server/tools/search_knowledge.py
retrieval/query.py
main.py
```

during this phase.

The legacy Budgeter and new Budgeting Layer must remain independently testable.

### Required Verification

Run:

```text
python -m pytest tests/budgeting -v
python -m pytest tests/integration -v
python -m pytest tests/retriever -v
python -m pytest tests/planner -v
python -m pytest
```

The existing validated baseline is:

```text
Planner     = 52
Retriever   = 84
Integration = 48

Existing baseline = 184 passing tests
```

No existing test regression is allowed.

### Implementation Completion Report

After implementation, report:

```text
1. New files created
2. Existing files modified
3. Public API exposed
4. Final BudgetedContext structure
5. Final BudgetMetadata structure
6. Allocation algorithm implemented
7. Query overflow behavior implemented
8. Unit truncation behavior implemented
9. Validation behavior implemented
10. Test counts by subsystem
11. Full-suite result
12. Any deviation from this document
```

Any deviation must be explicitly identified.

Do not silently change the architecture to simplify implementation.

### Final Architecture Status

**CONTEXT BUDGETING V1 — FROZEN**

This document is the authoritative implementation contract for the V1 Context Budgeting Layer.
