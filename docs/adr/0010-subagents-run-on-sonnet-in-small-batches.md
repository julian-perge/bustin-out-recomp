# ADR-0010: Namer and reviewer agents run on Sonnet, in batches of 25 functions

- **Status:** Accepted (user decision)
- **Date:** 2026-10-12

## Context

M2b batches 4 to 8 ran each batch of 50 functions through one Opus namer and one Opus reviewer. Those five batches used up a 5-hour usage window in about an hour: 56.8M cache-read tokens in 63 minutes, 83% of them in the Opus subagents. Each agent's context grew from about 24k to about 200k tokens over its batch, so every later tool call re-read a large context.

## Decision

- The `namer` and `reviewer` agents run on Sonnet. The reviewer runs at effort medium. Both are set in the frontmatter of `.claude/agents/namer.md` and `.claude/agents/reviewer.md`.
- A batch of 50 functions is split between two namers of 25 (`names batch 2N-1|2N --size 25`), so neither agent's context grows as large.
- The reviewer decompiles only the names that go beyond what their strings say.
- Agents read only the lines of a file they need, not whole documents.

## Consequences

- From batch 9 on, M2b ran under this rule. Batches 9 to 15 and the follow-up pass named 229 functions, and the reviewer changed or cleared 17. Batches 1 to 8 named 263 and the reviewer changed 12.
- A Sonnet agent can miss what an Opus agent would catch. The reviewer step stays, and the lead checks `git diff` and `sync check` after each review.
