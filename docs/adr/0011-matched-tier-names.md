# ADR-0011: A matched function takes the `matched` tier, with its source file as evidence

- **Status:** Accepted (user decision)
- **Date:** 2026-10-12

## Context

ADR-0009 names a function when it is matched and leaves open how that name is recorded in `config/symbols.txt`, whose rows carry a tier and evidence (ADR-0002). The GameCube decomp (daftblazer/bustin-out-decomp) records no tier or evidence: `tools/rename.py` replaces the `fn_XXXXXXXX` entry in `config/G4ME69/symbols.txt` with the mangled name the compiler emits, and `configure.py` marks match status per object file (`Object(Matching, ...)` or `Object(NonMatching, ...)`). The C++ that compiles to the original bytes is the evidence.

## Decision

- A function whose C++ compiles to its original bytes gets the tier `matched`. It outranks `sdk`, `gc`, `string` and `auto` for game functions.
- Its evidence is the path of the source file that holds the match, for example `src/sims/ESimsApp.cpp`.
- Its name is the VC71 decorated name the compiler emits for that function, so that `symbols.txt` holds the name the re-link pairs against. Tools that show names to people demangle it.
- The lead records a matched name only after its function has passed the full gate on `main`. `names set` checks that the source file exists and that `config/functions.csv`, which `bodecomp.match` writes, lists the function as `matched` from that file.
- A matched function whose source uses placeholder names, such as a stand-in struct `S_00018390` or a method `fn_00018390`, keeps its `auto` name; only `config/functions.csv` records the match (user ruling, 2026-10-12, M3 batch 1). A decorated name built from placeholders is not evidence of a name and would outrank every other tier.
- A `matched` name replaces any earlier `gc`, `string` or `auto` name. When the replaced name was not `auto`, the evidence keeps it after the path, for example `src/sims/ESimsApp.cpp was:ParseCommandLine`.

## Consequences

- `bodecomp.ledger` reports match status from `config/functions.csv` in its own table, so a matched function with an `auto` name still counts as matched. It also reports `matched` as a name tier, and `bodecomp.names set` records a matched name when its evidence is a `src/` path (docs/WORKFLOW.md, "Matched names"). `names set` and `names check` refuse a function that `config/functions.csv` does not list as `matched` from the cited source (M3).
- Whether Ghidra and `sync apply` keep a decorated name such as `?parseCommandLine@ESimsApp@@QAEXXZ` unchanged has not been checked (compare F-0032).
- This settles the open point in ADR-0009's Consequences on how a matched name is recorded.
