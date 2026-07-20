# PROMPT BUILDER

Version: 1.0
Status: Production Ready
Architecture Status: Frozen
Production Target: Production V1
Current Phase: Production V1 Freeze
Review Requirement: Architecture Review Required Before Modification

------------------------------------------------------------------------

## Part 1 --- Purpose

The Prompt Builder is the deterministic transformation layer between
Context Budgeting and downstream model routing or model execution.

Its responsibility is:

> Transform an immutable `BudgetedContext` into an immutable,
> deterministic, model-ready `Prompt`.

The Prompt Builder exists to preserve the AI Ecosystem mission of
reducing unnecessary token usage before inference while maintaining
clear subsystem ownership.

The Prompt Builder does not decide what information is relevant.

The Prompt Builder does not decide how much context fits.

The Prompt Builder does not retrieve information.

The Prompt Builder does not select a model.

The Prompt Builder only assembles context already approved by the
Context Budgeting Layer into the canonical prompt representation.

### Canonical Pipeline Position

``` text
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
PromptBuilder
  ↓
Prompt
  ↓
Future Model Router / Model Execution
```

Planner, Retriever, Retriever Integration, and Context Budgeting are
frozen upstream V1 subsystems.

Prompt Builder must consume their contracts without redesigning or
reinterpreting them.

### Architectural Invariants

> Prompt Builder is a deterministic domain transformation.

> `BudgetedContext` is the canonical Prompt Builder input.

> `Prompt` is the canonical Prompt Builder output.

> Prompt Builder never performs retrieval, budgeting, routing, or model
> execution.

> Prompt Builder never mutates upstream domain objects.

------------------------------------------------------------------------

## Part 2 --- Scope and Ownership

### Prompt Builder Owns

The Prompt Builder owns:

-   Prompt domain contract
-   Deterministic prompt assembly
-   Fixed prompt section order
-   Empty-section omission
-   Prompt formatting
-   Effective-query placement
-   Exact final-prompt token validation
-   Prompt Builder boundary validation
-   Prompt Builder exceptions
-   Stable Prompt serialization

### Prompt Builder Does Not Own

The Prompt Builder does not own:

-   Query analysis
-   Complexity classification
-   Retrieval decisions
-   Knowledge retrieval
-   Memory retrieval
-   Session retrieval
-   Context relevance
-   Context ranking
-   Context reranking
-   Context deduplication
-   Context truncation
-   Context allocation
-   Category caps
-   Budget redistribution
-   Query truncation
-   Model selection
-   Tool selection
-   Provider selection
-   Model invocation
-   LLM response generation
-   Infrastructure adaptation
-   ChromaDB access
-   MCP execution
-   Legacy RAG migration

### Responsibility Boundary

``` text
Context Budgeting
    owns:
        context reduction
        token allocation
        controlled truncation
        effective query
        budget metadata

Prompt Builder
    owns:
        deterministic textual assembly
        prompt contract
        exact final prompt validation

Model Router / Execution
    owns:
        downstream model decision
        provider/model execution
```

### Architectural Invariants

> Context selection remains upstream.

> Token allocation remains upstream.

> Prompt construction belongs only to Prompt Builder.

> Model execution remains downstream.

------------------------------------------------------------------------

## Part 3 --- Canonical Input Contract

### Input

The only Prompt Builder context input is:

``` text
BudgetedContext
```

Canonical owner:

``` text
Context Budgeting Layer
```

The Prompt Builder consumes the existing `BudgetedContext` contract.

It must not redefine, duplicate, wrap, or replace that contract.

### Public Build Contract

``` text
PromptBuilder.build(
    budgeted_context: BudgetedContext
) -> Prompt
```

No separate query parameter is accepted.

Rejected contract:

``` text
PromptBuilder.build(
    budgeted_context: BudgetedContext,
    query: str
) -> Prompt
```

### Query Authority

`BudgetedContext.effective_query` is the only query authority for Prompt
Builder.

Reason:

The Context Budgeting Layer may truncate the original query under its
explicit overflow policy.

The effective query used for token accounting must be the same query
passed downstream.

A separate query argument would create two possible query authorities
and permit disagreement.

Therefore:

``` text
Prompt query source
    =
BudgetedContext.effective_query
```

Prompt Builder must not:

-   Receive the original query separately
-   Reconstruct the original query
-   Prefer another query source
-   Rewrite the effective query
-   Expand the effective query
-   Correct the effective query
-   Normalize the effective query
-   Truncate the effective query

### Input Validation Boundary

Prompt Builder validates only assumptions required at its boundary:

-   Input is a `BudgetedContext`
-   `BudgetedContext.version` is supported
-   `effective_query` is a string
-   `effective_query` is not empty
-   `effective_query` is not whitespace-only

Prompt Builder must not duplicate the full `BudgetValidator`.

It must not revalidate:

-   Budget category arithmetic
-   `remaining_tokens`
-   Category token sums
-   Budget redistribution
-   Query truncation policy
-   Retriever contracts
-   Retrieval metadata
-   Upstream allocation correctness

Those invariants are owned by frozen upstream subsystems.

### Architectural Invariants

> `BudgetedContext` is the single Prompt Builder input contract.

> `effective_query` is the single query authority.

> Prompt Builder validates its boundary without duplicating Budgeting
> ownership.

------------------------------------------------------------------------

## Part 4 --- Canonical Output Contract

### Prompt

The Prompt Builder returns:

``` text
Prompt
```

Recommended V1 domain contract:

``` text
Prompt

content: str
version: int
```

Conceptual representation:

``` python
@dataclass(frozen=True)
class Prompt:
    content: str
    version: int = CURRENT_SCHEMA_VERSION
```

### Field Ownership

#### `content`

The exact deterministic model-ready textual prompt assembled from
`BudgetedContext`.

#### `version`

The Prompt schema version.

V1:

``` text
version = 1
```

### Immutability

`Prompt` must be immutable after construction.

### Stable Serialization

`Prompt.to_dict()` must return a stable explicit representation:

``` text
{
    "content": "...",
    "version": 1
}
```

Serialization must not depend on unordered runtime state.

### Fields Not Included in V1

Do not add:

-   `token_count`
-   `sections`
-   `model`
-   `provider`
-   `query`
-   `knowledge_count`
-   `memory_count`
-   `session_count`
-   `created_at`
-   `prompt_id`
-   `template_id`
-   `metadata`

Reasons:

-   Token count is derivable by the shared token counter.
-   Category counts and budget diagnostics belong upstream.
-   Model and provider belong to routing/execution.
-   Query is already represented inside the assembled content and owned
    upstream as `effective_query`.
-   Timestamps break replay equality.
-   Prompt IDs are operational concerns.
-   Template IDs have no proven V1 consumer.
-   Generic metadata creates an unowned extension surface.

These fields may be reconsidered only when a concrete downstream
requirement exists.

### Architectural Invariants

> `Prompt` is immutable.

> `Prompt` is versioned.

> `Prompt` contains only stable Prompt Builder domain state.

> Operational and routing state do not enter the Prompt contract.

------------------------------------------------------------------------

## Part 5 --- Package Architecture

### Production Package

``` text
prompt_builder/
│
├── __init__.py
├── exceptions.py
├── prompt.py
├── prompt_builder.py
└── prompt_validator.py
```

### Test Package

``` text
tests/prompt_builder/
│
├── test_prompt.py
├── test_prompt_builder.py
├── test_prompt_validator.py
└── test_prompt_builder_pipeline.py
```

### `prompt.py`

Owns:

``` text
Prompt
CURRENT_SCHEMA_VERSION
```

Responsibilities:

-   Define immutable Prompt contract
-   Define Prompt schema version
-   Provide stable explicit serialization

Must not:

-   Assemble prompts
-   Count tokens
-   Validate `BudgetedContext`
-   Call infrastructure

### `prompt_builder.py`

Owns:

``` text
PromptBuilder
```

Responsibilities:

-   Accept `BudgetedContext`
-   Validate Prompt Builder input
-   Assemble prompt sections
-   Preserve upstream order
-   Omit empty context sections
-   Emit effective query
-   Construct `Prompt`
-   Validate final Prompt
-   Return Prompt

Must not:

-   Retrieve
-   Rerank
-   Deduplicate
-   Truncate
-   Budget
-   Summarize
-   Route
-   Call an LLM
-   Access infrastructure
-   Mutate `BudgetedContext`

### `prompt_validator.py`

Owns:

``` text
PromptValidator
```

Responsibilities:

-   Validate Prompt Builder input boundary
-   Validate Prompt output contract
-   Validate exact final prompt token limit

The validator must be pure except for deterministic use of the injected
or shared token-counting callable.

It must not:

-   Mutate
-   Repair
-   Truncate
-   Retrieve
-   Read configuration
-   Access filesystem
-   Access database
-   Call a model

### `exceptions.py`

Owns:

``` text
PromptBuilderError
PromptValidationError
```

Hierarchy:

``` text
PromptBuilderError
        ↑
PromptValidationError
```

`PromptBuilderError` is the base Prompt Builder exception.

`PromptValidationError` represents invalid Prompt Builder input, invalid
Prompt output, unsupported Prompt Builder contract version, or final
prompt budget violation.

No separate `PromptConstructionError` is introduced in V1.

Deterministic string assembly does not currently define a distinct
stable failure concept beyond validation failure.

### `__init__.py`

Public V1 API:

``` text
Prompt
PromptBuilder
PromptBuilderError
PromptValidationError
```

`PromptValidator` remains internal unless a proven downstream consumer
requires direct validation access.

### Rejected V1 Abstractions

Do not introduce:

``` text
prompt_formatter.py
prompt_template.py
prompt_section.py
prompt_metadata.py
prompt_optimizer.py
prompt_strategy.py
prompt_factory.py
prompt_config.py
```

These abstractions have no proven V1 requirement and fail the No Regret
Rule.

### Architectural Invariants

> The package remains small and locally understandable.

> Each production file has one clear responsibility.

> Speculative extension abstractions are prohibited.

------------------------------------------------------------------------

## Part 6 --- Deterministic Prompt Format

### Fixed Section Order

The V1 section order is permanently fixed as:

``` text
Knowledge
Memory
Session
Query
```

Canonical textual form:

``` text
[KNOWLEDGE]
<knowledge content>

[MEMORY]
<memory content>

[SESSION]
<session content>

[QUERY]
<effective query>
```

### Section Separator

Non-empty sections are joined by exactly:

``` text
\n\n
```

The implementation must use one explicit deterministic separator.

No environment-specific line separator may be used.

Use `\n`, not `os.linesep`.

### Section Labels

V1 section labels are exactly:

``` text
[KNOWLEDGE]
[MEMORY]
[SESSION]
[QUERY]
```

Labels are fixed contract-level formatting.

They must not be localized, renamed, dynamically configured, or selected
by model/provider in V1.

### Query Position

The Query section is always emitted.

The Query section is always last.

### Empty Category Policy

An empty context category produces no section.

Examples:

``` text
knowledge empty
    ↓
no [KNOWLEDGE] section
```

``` text
memory empty
    ↓
no [MEMORY] section
```

``` text
session empty
    ↓
no [SESSION] section
```

If all context categories are empty:

``` text
[QUERY]
<effective query>
```

Prompt Builder must not emit empty headings because they consume tokens
without carrying information.

### No System Instruction in V1

Prompt Builder V1 does not add a system instruction.

It does not add:

-   Assistant persona
-   Answer style
-   Safety policy
-   Model-specific instructions
-   Citation instructions
-   Tool instructions
-   Response format constraints

Those concerns require explicit future ownership and downstream contract
design.

They must not be invented inside Prompt Builder V1.

### Architectural Invariants

> Section order is fixed.

> Section labels are fixed.

> Empty context sections are omitted.

> Query is always present and last.

> Prompt formatting is provider independent.

> Prompt Builder V1 adds no system instruction.

------------------------------------------------------------------------

## Part 7 --- Knowledge Assembly

### Input Source

``` text
budgeted_context.knowledge.items
```

### Assembly Rule

For every `KnowledgeItem` in existing order:

``` text
append item.text
```

Knowledge item texts are joined using:

``` text
\n
```

Result:

``` text
[KNOWLEDGE]
<item.text>
<item.text>
<item.text>
```

### Preserved Property

The exact upstream item order is preserved.

Prompt Builder must not:

-   Sort by score
-   Sort by source
-   Sort by length
-   Group by source
-   Rerank
-   Deduplicate
-   Truncate
-   Summarize

### Emitted Fields

V1 emits:

``` text
KnowledgeItem.text
```

V1 does not emit by default:

-   `source`
-   `score`
-   item metadata

Reason:

These are retrieval or diagnostic fields and add prompt tokens without a
proven general V1 reasoning benefit.

Their upstream contracts remain unchanged.

### Text Preservation

Prompt Builder must preserve each item text exactly as received.

It must not call:

-   `strip()`
-   `lower()`
-   whitespace normalization
-   punctuation normalization
-   Unicode normalization

Upstream text is already the selected budgeted payload.

Prompt Builder adds only its own deterministic separators and section
labels.

### Architectural Invariants

> Knowledge order is preserved.

> Knowledge text is preserved.

> Retriever diagnostics are not automatically emitted.

------------------------------------------------------------------------

## Part 8 --- Memory Assembly

### Input Source

``` text
budgeted_context.memory.entries
```

### Assembly Rule

For every `MemoryEntry` in existing order:

``` text
append entry.content
```

Memory entry contents are joined using:

``` text
\n
```

Result:

``` text
[MEMORY]
<entry.content>
<entry.content>
```

### Preserved Property

The exact upstream entry order is preserved.

Prompt Builder must not:

-   Rerank memories
-   Group memories
-   Deduplicate memories
-   Truncate memories
-   Summarize memories
-   Add numbering

### Emitted Fields

V1 emits:

``` text
MemoryEntry.content
```

Memory infrastructure metadata is not emitted.

### Text Preservation

Memory content is preserved exactly as received.

No trimming or normalization is performed.

### Architectural Invariants

> Memory order is preserved.

> Memory content is preserved.

> Prompt Builder does not reinterpret memory relevance.

------------------------------------------------------------------------

## Part 9 --- Session Assembly

### Input Source

``` text
budgeted_context.session
```

The Context Budgeting contract preserves session semantic order:

``` text
Session summary
Recent messages in existing order
```

Prompt Builder preserves that order.

### Session Summary

If the session summary is non-empty:

``` text
Summary: <summary>
```

The literal prefix is:

``` text
Summary: 
```

The summary text itself is preserved exactly.

If summary is empty, no summary line is emitted.

### Recent Messages

For each recent message in existing order:

``` text
<role>: <content>
```

The exact role value is preserved.

The exact content value is preserved.

Example:

``` text
[SESSION]
Summary: User is designing the AI Ecosystem control plane.
user: Explain the Retriever.
assistant: The Retriever executes retrieval decisions.
```

### Session Section Presence

The Session section is emitted if at least one of the following exists:

-   Non-empty summary
-   At least one recent message

Otherwise the Session section is omitted.

### Forbidden Session Transformations

Prompt Builder must not:

-   Summarize messages
-   Merge messages
-   Remove messages
-   Reverse messages
-   Truncate messages
-   Normalize roles
-   Rename roles
-   Add timestamps
-   Add message indexes

### Architectural Invariants

> Session summary precedes recent messages.

> Recent-message order is preserved.

> Message roles are preserved.

> Message content is preserved.

------------------------------------------------------------------------

## Part 10 --- Query Assembly

### Query Source

The only query source is:

``` text
budgeted_context.effective_query
```

### Assembly

``` text
[QUERY]
<effective_query>
```

### Query Rules

The query is:

-   Always emitted
-   Always last
-   Preserved exactly
-   Never rewritten
-   Never expanded
-   Never normalized
-   Never truncated by Prompt Builder

Prompt Builder must not receive the original query.

### Architectural Invariant

> The query payload emitted by Prompt Builder is exactly
> `BudgetedContext.effective_query`.

This invariant is guaranteed by deterministic builder construction and
verified by builder tests.

Runtime substring occurrence counting must not be used to validate query
ownership because the same text may legitimately appear in context.

------------------------------------------------------------------------

## Part 11 --- Token Accounting and Budget Safety

### Shared Token Counter

Prompt Builder uses the same shared token-counting capability used by
Context Budgeting:

``` text
shared.token_counter
```

The builder or validator must support deterministic token-counter
injection for isolated tests, consistent with existing subsystem
testability patterns.

Default production behavior uses:

``` text
shared.token_counter.token_counter.count
```

### Exact Final Prompt Counting

Prompt Builder must assemble the exact final prompt first.

Then it counts:

``` text
token_counter.count(prompt.content)
```

The canonical final invariant is:

``` text
final_prompt_tokens <= budgeted_context.metadata.total_budget
```

### Why Final Prompt Counting Is Required

Tokenization is not assumed to be additive.

The architecture must not assume:

``` text
tokens(A + B) == tokens(A) + tokens(B)
```

Section labels, separators, role prefixes, and token boundaries may
affect the exact final token count.

Therefore Prompt Builder must not calculate prompt overhead using:

``` text
tokens(prompt)
- query_tokens
- used_context_tokens
```

That subtraction is not a safe semantic measurement of formatting
overhead.

### Reserved Tokens

`BudgetMetadata.reserved_tokens` records the budget reserved upstream
for Prompt Builder overhead.

Prompt Builder does not recalculate Context Budgeting allocation.

Prompt Builder does not enforce a derived:

``` text
calculated_overhead <= reserved_tokens
```

invariant through token subtraction.

Instead, the final system safety invariant is validated against the
exact assembled prompt:

``` text
tokens(final prompt) <= total_budget
```

### Reservation Compatibility

A `BudgetedContext` may be valid under Budgeting invariants while its
exact assembled Prompt exceeds `total_budget` if the configured
reservation is insufficient for actual Prompt Builder formatting under
the active token counter.

This is not repaired by Prompt Builder.

It is an explicit cross-layer compatibility failure.

Prompt Builder raises `PromptValidationError`.

The failure indicates that the upstream `reserved_budget` configuration
and the frozen Prompt Builder format are incompatible for that
execution.

Future application control-flow design may define how such configuration
failures are surfaced operationally.

Prompt Builder itself must not retry Context Budgeting or alter upstream
budgets.

### Overflow Behavior

If:

``` text
token_counter.count(prompt.content)
>
budgeted_context.metadata.total_budget
```

then:

``` text
raise PromptValidationError
```

Prompt Builder must not:

-   Remove knowledge
-   Remove memory
-   Remove session
-   Truncate query
-   Truncate context
-   Compress sections
-   Retry budgeting
-   Increase total budget

Those are not Prompt Builder responsibilities.

### Architectural Invariants

> Exact final prompt tokens are counted after assembly.

> Final prompt tokens must not exceed `total_budget`.

> Token-limit violations fail explicitly.

> Prompt Builder never repairs a budget violation by changing content.

> Reservation incompatibility is exposed, not hidden.

------------------------------------------------------------------------

## Part 12 --- Validation Architecture

### Validation Ownership

Prompt Builder validates its own input assumptions and output
invariants.

It does not replace Context Budgeting validation.

### Input Validation

`PromptValidator.validate_input()` validates:

``` text
budgeted_context is BudgetedContext
BudgetedContext.version is supported
effective_query is str
effective_query is not empty
effective_query is not whitespace-only
```

Invalid input must not be silently repaired.

### Output Validation

`PromptValidator.validate_output()` validates:

``` text
prompt is Prompt
prompt.content is str
prompt.content is not empty
prompt.content is not whitespace-only
prompt.version is supported
exact final prompt token count <= total_budget
```

The validator requires the source `BudgetedContext` or explicit
`total_budget` needed to validate the final prompt limit.

Recommended V1 contract:

``` text
PromptValidator.validate_output(
    prompt: Prompt,
    total_budget: int
) -> None
```

The validator does not need the entire `BudgetedContext` for output
validation.

This keeps validation dependency narrow.

### Validation Must Not Duplicate

Prompt Validator must not validate:

-   `used_context_tokens <= context_budget`
-   Category token sums
-   `remaining_tokens`
-   Category token counts
-   Query truncation arithmetic
-   Retrieval object correctness
-   Retrieval metadata correctness

These are upstream invariants.

### Query Source Validation

Prompt Validator must not count occurrences of `effective_query` inside
`Prompt.content`.

The same text may legitimately appear in knowledge, memory, or session
context.

Query source correctness is a deterministic builder responsibility and
must be tested through exact expected prompt construction.

### Failure Behavior

Prompt Builder fails explicitly.

It must not:

-   Catch broad exceptions and return an empty Prompt
-   Return a partial Prompt
-   Replace invalid input with defaults
-   Silently increase budget
-   Silently omit selected context
-   Silently rewrite the query

### Architectural Invariants

> Prompt validation owns Prompt Builder invariants only.

> Budget validation remains owned by Context Budgeting.

> Invalid Prompt Builder state fails explicitly.

------------------------------------------------------------------------

## Part 13 --- Determinism and Non-Mutation

### Determinism

For identical `BudgetedContext` and identical token-counter behavior:

``` text
PromptBuilder.build(context)
```

must produce identical:

``` text
Prompt.content
Prompt.version
Prompt.to_dict()
```

### Forbidden Nondeterminism

Prompt construction must not depend on:

-   Timestamps
-   UUIDs
-   Random values
-   Set iteration
-   Unordered semantic iteration
-   Runtime latency
-   Environment state
-   Provider state
-   Model state

### Non-Mutation

Prompt Builder must not mutate:

``` text
BudgetedContext
KnowledgeContext
KnowledgeItem
MemoryContext
MemoryEntry
SessionContext
SessionMessage
BudgetMetadata
```

The Prompt Builder only reads the upstream immutable contract and
constructs a new immutable Prompt.

### Architectural Invariants

> Identical inputs produce identical Prompt output.

> Prompt construction is replayable.

> Upstream contracts remain unchanged.

------------------------------------------------------------------------

## Part 14 --- Dependency Direction

### Allowed Dependencies

``` text
prompt_builder
    ↓
budgeting
```

Reason:

Prompt Builder consumes the canonical `BudgetedContext` contract.

``` text
prompt_builder
    ↓
shared.token_counter
```

Reason:

Prompt Builder must validate the exact final prompt token count using
the shared token-counting capability.

### Transitive Contract Access

`BudgetedContext` contains:

``` text
KnowledgeContext
MemoryContext
SessionContext
BudgetMetadata
```

Prompt Builder may traverse these nested objects through the
`BudgetedContext` contract.

This does not authorize Prompt Builder to call Retriever components or
infrastructure.

### Forbidden Dependencies

Prompt Builder must not depend on:

``` text
planner
integration
retrieval
memory infrastructure
conversation_memory infrastructure
llm
routing
mcp_server
services
ChromaDB
model providers
```

### No Legacy Budgeter Dependency

Prompt Builder must not import:

``` text
services/context_budgeter.py
ContextItem
```

The legacy ContextItem-based budgeter remains isolated to legacy
consumers until migration and verified removal.

### Architectural Invariants

> Dependency direction follows the canonical control flow.

> Prompt Builder depends on stable domain contracts and shared token
> counting only.

> Prompt Builder remains infrastructure independent.

------------------------------------------------------------------------

## Part 15 --- Prompt Builder Execution Algorithm

Canonical V1 algorithm:

``` text
1. Receive BudgetedContext.

2. PromptValidator.validate_input(budgeted_context).

3. Initialize an empty ordered section collection.

4. If knowledge contains items:
       assemble KNOWLEDGE section
       preserving item order and exact item text.

5. If memory contains entries:
       assemble MEMORY section
       preserving entry order and exact entry content.

6. If session contains a non-empty summary or recent messages:
       assemble SESSION section.
       summary first.
       recent messages second.
       preserve message order, role, and content.

7. Assemble QUERY section
       from budgeted_context.effective_query.

8. Join sections using the fixed "\n\n" separator.

9. Construct immutable Prompt.

10. PromptValidator.validate_output(
        prompt,
        budgeted_context.metadata.total_budget
    ).

11. Return Prompt.
```

### Complexity

Let:

``` text
K = knowledge items
M = memory entries
S = session messages
T = total prompt text/token counting cost
```

Prompt assembly is linear in selected units and text processed:

``` text
O(K + M + S + T)
```

No sorting is performed.

No retrieval is performed.

No model call is performed.

### Architectural Invariants

> Prompt Builder performs one deterministic forward transformation.

> Prompt Builder introduces no hidden control loop.

------------------------------------------------------------------------

## Part 16 --- Public API

### Package Public API

``` text
from prompt_builder import (
    Prompt,
    PromptBuilder,
    PromptBuilderError,
    PromptValidationError,
)
```

### Primary API

``` text
PromptBuilder.build(
    budgeted_context: BudgetedContext
) -> Prompt
```

### Constructor Testability

Recommended conceptual constructor:

``` text
PromptBuilder(
    token_counter: Callable[[str], int] | None = None
)
```

If no token counter is injected, use the shared token counter.

The injection point exists for deterministic isolated testing.

It is not a token-provider abstraction or strategy system.

### Validator Visibility

`PromptValidator` is internal in V1.

Do not export it from the package root unless a concrete consumer
requires direct validator access.

### Architectural Invariants

> Public API surface is minimal.

> Testability does not require speculative abstraction.

------------------------------------------------------------------------

## Part 17 --- Testing Architecture

### `test_prompt.py`

Must cover:

-   Prompt creation
-   Frozen behavior
-   Default schema version
-   Explicit supported version behavior as applicable
-   Stable `to_dict()`
-   Exact serialization key structure
-   Exact serialization key order

### `test_prompt_validator.py`

Must cover input validation:

-   Valid `BudgetedContext`
-   Non-`BudgetedContext` rejected
-   Unsupported `BudgetedContext.version` rejected
-   Non-string effective query rejected
-   Empty effective query rejected
-   Whitespace-only effective query rejected

Must cover output validation:

-   Valid Prompt accepted
-   Non-Prompt rejected
-   Non-string content rejected where constructible
-   Empty content rejected
-   Whitespace-only content rejected
-   Unsupported Prompt version rejected
-   Prompt exactly at total budget accepted
-   Prompt above total budget rejected
-   Token-counter behavior is deterministic

### `test_prompt_builder.py`

Must cover:

-   Query-only prompt
-   Knowledge-only context plus query
-   Memory-only context plus query
-   Session-summary-only context plus query
-   Session-messages-only context plus query
-   Full context prompt
-   Fixed section order
-   Empty knowledge section omitted
-   Empty memory section omitted
-   Empty session section omitted
-   Query always emitted
-   Query always last
-   `effective_query` used exactly as query payload
-   Knowledge item order preserved
-   Knowledge text preserved exactly
-   Knowledge source not emitted
-   Knowledge score not emitted
-   Memory entry order preserved
-   Memory content preserved exactly
-   Session summary precedes messages
-   Session message order preserved
-   Session role preserved
-   Session content preserved
-   Input `BudgetedContext` not mutated
-   Identical input produces identical Prompt
-   Exact expected Prompt content
-   Final prompt within total budget accepted
-   Final prompt above total budget rejected
-   Builder does not silently truncate on overflow

### `test_prompt_builder_pipeline.py`

Cross-layer tests must cover:

``` text
RetrievedContext
    ↓
ContextBudgeter
    ↓
BudgetedContext
    ↓
PromptBuilder
    ↓
Prompt
```

Required cases:

-   Budgeted knowledge reaches Prompt in preserved order
-   Budgeted memory reaches Prompt in preserved order
-   Budgeted session reaches Prompt in preserved order
-   Truncated effective query from Budgeter is the Prompt query
-   Context omitted by Budgeter does not reappear
-   Prompt Builder does not modify BudgetedContext
-   Exact final Prompt respects total budget
-   Insufficient Prompt reservation produces explicit Prompt validation
    failure
-   Repeated cross-layer execution is deterministic

### Regression Validation

After implementation:

``` text
1. Run tests/prompt_builder/
2. Run Budgeting → Prompt Builder cross-layer tests
3. Run existing Planner tests
4. Run existing Retriever tests
5. Run existing Integration tests
6. Run existing Context Budgeting tests
7. Run full pytest suite
```

The validated pre-Prompt-Builder baseline is:

``` text
249 passed
0 failures
1 external ChromaDB deprecation warning
```

Any unrelated regression blocks acceptance.

### Architectural Invariants

> Tests verify contracts, boundaries, determinism, non-mutation, and
> token safety.

> Cross-layer tests prove the frozen upstream handoff.

------------------------------------------------------------------------

## Part 18 --- Acceptance Criteria

Prompt Builder V1 is accepted only when all conditions are true.

### Contract

-   `BudgetedContext` is the only Prompt Builder input.
-   `effective_query` is the only query authority.
-   `Prompt` is immutable.
-   `Prompt` is versioned.
-   `Prompt.to_dict()` is stable.

### Assembly

-   Section order is Knowledge → Memory → Session → Query.
-   Empty context sections are omitted.
-   Query is always emitted.
-   Query is always last.
-   Knowledge order is preserved.
-   Memory order is preserved.
-   Session summary precedes recent messages.
-   Session message order is preserved.
-   Upstream text payloads are preserved exactly.

### Token Safety

-   Exact final Prompt content is token-counted.
-   Final Prompt tokens do not exceed `total_budget`.
-   Non-additive tokenizer behavior is not approximated through
    subtraction.
-   Budget overflow fails explicitly.
-   Prompt Builder does not truncate or omit selected content to repair
    overflow.

### Ownership

-   Prompt Builder performs no retrieval.
-   Prompt Builder performs no budgeting.
-   Prompt Builder performs no routing.
-   Prompt Builder performs no model execution.
-   Prompt Builder does not duplicate Budget Validator ownership.
-   Prompt Builder has no legacy ContextItem dependency.
-   Prompt Builder has no infrastructure dependency.

### Quality

-   Subsystem tests pass.
-   Cross-layer tests pass.
-   Full regression suite passes.
-   No frozen upstream subsystem is redesigned.
-   Documentation and implementation agree.
-   No speculative V1 abstraction is introduced.

------------------------------------------------------------------------

## Part 19 --- Migration and Integration Boundary

Prompt Builder implementation and application control-flow migration are
separate engineering changes.

During initial Prompt Builder implementation, do not wire Prompt Builder
into legacy production entry points unless explicitly authorized.

Do not modify:

``` text
llm/rag.py
mcp_server/server.py
mcp_server/tools/search_knowledge.py
retrieval/query.py
main.py
```

as part of the isolated Prompt Builder implementation phase.

### Sequence

``` text
1. Freeze Prompt Builder architecture.
2. Implement Prompt Builder package.
3. Review every Prompt Builder production file.
4. Run Prompt Builder subsystem tests.
5. Run Context Budgeting → Prompt Builder cross-layer tests.
6. Run full regression suite.
7. Update CHANGELOG.md.
8. Update Project_snapshot.md.
9. Update AI_ECOSYSTEM_BOOTSTRAP.md.
10. Design the new application control flow.
11. Wire Planner → RetrieverIntegration → ContextBudgeter → PromptBuilder.
12. Validate the complete new control path.
13. Migrate local RAG entry point.
14. Migrate MCP entry point.
15. Trace legacy Budgeter consumers.
16. Remove legacy consumers only after verified dependency tracing.
```

### Architectural Invariants

> Prompt Builder implementation does not silently migrate application
> entry points.

> New subsystem validation precedes production wiring.

> Legacy migration remains a separate controlled change.

------------------------------------------------------------------------

## Part 20 --- Frozen V1 Architectural Decisions

The following decisions are frozen for Prompt Builder V1:

> `BudgetedContext` is the canonical and only Prompt Builder input.

> `BudgetedContext.effective_query` is the only query authority.

> `PromptBuilder.build(BudgetedContext) -> Prompt` is the canonical
> public transformation.

> `Prompt` contains `content` and `version`.

> `Prompt` is immutable and versioned.

> Prompt section order is Knowledge → Memory → Session → Query.

> Empty context categories produce no section.

> Query is always emitted and always last.

> Knowledge emits item text only.

> Memory emits entry content only.

> Session emits summary first and recent messages second.

> Upstream unit order is preserved.

> Upstream text payloads are preserved exactly.

> Prompt Builder does not retrieve, rerank, deduplicate, summarize,
> truncate, budget, route, or execute models.

> Prompt Builder adds no system instruction in V1.

> Prompt Builder uses fixed provider-independent section labels.

> Prompt Builder counts the exact fully assembled Prompt.

> Final Prompt token count must not exceed
> `BudgetMetadata.total_budget`.

> Token additivity is not assumed.

> Formatting overhead is not derived by subtracting separately counted
> token totals.

> `reserved_tokens` remains an upstream reservation fact.

> Insufficient reservation that causes final Prompt overflow is an
> explicit cross-layer compatibility failure.

> Prompt Builder never repairs budget overflow by changing content.

> Prompt Validator owns Prompt Builder boundary and Prompt invariants
> only.

> Budget Validator retains ownership of Budgeting arithmetic and
> allocation invariants.

> Prompt construction is deterministic.

> Prompt Builder does not mutate upstream domain objects.

> Prompt Builder depends only on the Budgeting contract and shared
> token-counting capability.

> Prompt Builder remains infrastructure independent.

> Prompt Builder implementation and legacy application migration are
> separate changes.

------------------------------------------------------------------------

## Architecture Freeze

Parts 1 through 20 define the frozen V1 Prompt Builder architecture.

Implementation must follow these decisions without introducing
alternative input contracts, query authorities, prompt formats,
token-overflow repair behavior, template systems, model-specific
formatting, or cross-layer dependencies.

Canonical V1 flow:

``` text
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
PromptBuilder
  ↓
Prompt
```

Canonical Prompt Builder contract:

``` text
PromptBuilder.build(
    budgeted_context: BudgetedContext
) -> Prompt
```

Canonical Prompt contract:

``` text
Prompt

content: str
version: int
```

Status:

``` text
PROMPT BUILDER V1 ARCHITECTURE FROZEN
```
