# ADR-0002: Text files are the source of truth; Ghidra is rebuilt from them

- **Status:** Accepted
- **Date:** 2026-10-10

## Context

A Ghidra project is binary, cannot be diffed or reviewed, and loses every name if it is damaged. Several agents need the same names.

## Decision

`config/symbols.txt` (tab-separated: address, kind, size, name, tier, evidence) is the record of every name. `uv run python -m bodecomp.sync export` copies names from Ghidra into it, `apply` copies them back, and `check` compares both ways. `tools/rebuild-ghidra.sh` rebuilds the project from `orig/default.xbe`, then `sync apply` restores the names. `ghidra/` is gitignored.

## Consequences

- A name that exists only in Ghidra is lost on a rebuild; `sync export` and a commit make it permanent. The rebuild script refuses to run while `config/symbols.txt` differs from the last commit.
- Every name carries a tier (`sdk`, `gc`, `string`, `matched` (ADR-0011), `auto`) and its evidence, so a name can be raised only with new evidence.
- `docs/LEDGER.md` is generated from the same file.
- Functions that Ghidra's analysis does not find on import are recreated from the function starts in `symbols.txt` by `tools/create-functions.sh`, which `tools/rebuild-ghidra.sh` runs after the import (M2a).
