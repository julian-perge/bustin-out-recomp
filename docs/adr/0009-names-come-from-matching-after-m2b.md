# ADR-0009: After M2b, functions are named when they are matched, not in separate naming passes

- **Status:** Accepted (user decision)
- **Date:** 2026-10-12

## Context

The design spec runs a naming phase (M2) before matching (M3) but records no reason for that order. Matching does not depend on names: a decompiled function is paired with its target by an address comment, and the build reads its mangled name from the compiled object (spec, "Symbol pairing"). M2b took 16 namer and reviewer rounds and 36 findings (F-0030 to F-0065) to set 496 string names (497 after M2b Task 7), and most of that effort went into settling names rather than into facts a matcher needs. A name given at match time comes from C++ that compiles to the original bytes, which is stronger evidence than a string-tier name, and it replaces any earlier name anyway.

The GameCube decomp (daftblazer/bustin-out-decomp, `CLAUDE.md`, section "Names") takes names only from the Sims 2 symbol map and from class-name strings. Every other function keeps its `fn_XXXXXXXX` placeholder until it is decompiled, and then takes the mangled name the compiler emits.

## Decision

- M2b is the last separate naming pass. From M3 on, a function gets its name when it is matched, from the C++ signature the matcher wrote.
- A function whose name would rest only on structure (a vtable slot, a call pattern) and on no string keeps its `auto` name, as in the GameCube repo. This covers 0x9F540, 0xA1B00 and 0x90310 at the end of M2b.
- The names M2 already set stay in `config/symbols.txt` as context for matchers.
- Open findings whose only next step is to choose a name (for example F-0042, F-0045, F-0047, F-0050) wait until their functions are matched.

## Consequences

- The `namer` agent is no longer part of the batch loop after M2b. Ghidra changes that matching needs, such as creating a missing function, are still made by one writer (ADR-0003).
- Matchers read more `FUN_` callees than they would after a full naming pass. The string names from M2b cover part of that.
- Choosing which functions to match first cannot rely on names alone; addresses, vtables and the existing names have to serve.
- How a matched name is recorded in `config/symbols.txt` is settled by ADR-0011.
