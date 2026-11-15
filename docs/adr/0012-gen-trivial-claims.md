# ADR-0012: gen_trivial reads claims from the sources and lists only unclaimed units

- **Status:** Accepted (lead ruling, M4 plan Task 3)
- **Date:** 2026-10-12

## Context

`bodecomp.trivial generate` writes sources for small functions under `src/game/trivial/`, and `shapes` lists the byte patterns left for a later pass. Both need to know which functions another source already claims. `config/functions.csv` records the last match run, but it can be stale when a source was added or removed since.

## Decision

- `generate` and `shapes` decide which functions are claimed with `bodecomp.match.scan`, which reads the address comments in `src/`, not with `config/functions.csv`. `generate` skips a function that a source outside `src/game/trivial/` claims, so it never writes a second claim that the match run would reject.
- `shapes` lists only units that no source claims, the trivial sources included. A shape name in its output therefore means that `generate` recognised the pattern and the build did not match it.

## Consequences

- Both commands read every source in `src/` on each run, which takes well under a second today.
- `shapes` output after a `generate` run shows only what is left, so its counts fall as passes are added.
