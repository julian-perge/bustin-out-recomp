# ADR-0013: A match never hand-writes code the compiler generates, and gen_trivial shapes are reviewed before use

- **Status:** Accepted (user decision, 2026-10-12)
- **Date:** 2026-10-12

## Context

`bodecomp.match` checks bytes and relocations, not whether the source is code a programmer wrote in 2003. During the F-0080 trial compiles the lead made the vtable-store shapes pass by writing the vtable pointer into a `void*` member by hand (`vtable = DAT_X;`), recorded that as matched, and reported it without flagging it. A side agent caught it. The real class form, with a virtual function named after slot 0 of the target vtable, also matched. The plausibility rule existed (design spec, `.claude/agents/reviewer.md`), but only the reviewer of matcher batches applied it. gen_trivial output and the lead's own trials go through no reviewer, and one gen_trivial shape writes hundreds of functions.

## Decision

- No source hand-writes what VC71 generates by itself: vtable pointer stores, this-adjusting and vtordisp thunks, exception-handling frames and state numbers, scalar and vector deleting destructors, or the calls to base and member constructors and destructors. A function that matches only with such code is parked with blocker class `source shape`, not matched.
- Placeholder names (`FUN_`, `S_`, `DAT_`) and placeholder types are still fine (ADR-0011). They stand in for names; the rule is about the structure of the code.
- Each new shape in `bodecomp.trivial.recognise`, and each change to an existing shape's source, gets one `reviewer` pass before `generate` runs with it. The reviewer gets the shape's generated source for one example address and that address's disassembly, and checks the source against the plausibility rule. Its verdict is recorded in the row for the shape in `docs/m4-results.md` or the results file of the milestone that adds it.

## Consequences

- Some functions that a hand-written form would match stay parked until their real class layout is known.
- A shape costs one reviewer run, once, instead of one per function it covers.
- The lead's trial compiles outside a batch have no reviewer; the lead applies the same rule to them and marks a trial result that needs compiler-generated code as a failure.
