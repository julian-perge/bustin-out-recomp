# ADR-0022: The functions hash of the sync stamp covers only the function starts

- **Status:** Accepted (user decision, 2026-11-17, issue #75)
- **Date:** 2026-11-17
- **Amends:** [ADR-0021](0021-generated-session-state-and-ghidra-freshness.md) points 8 and 9

## Context

ADR-0021 point 8 put the SHA-256 of the whole `function` lines of `config/symbols.txt` in `ghidra/.sync-stamp`. Point 9 made the hook ask for a rebuild when that hash changes.

A whole `function` line holds the name, size, tier and evidence columns too. So a function rename changed the hash, and the hook asked for a rebuild. Evidence: in the manual run of #65 in WSL, `bodecomp.names set` on one function made the hook print the rebuild line. `sync apply` and `sync check` then made it print `level`, with no rebuild. 3338 of the 21734 function lines had a non-auto name on 2026-11-17, so most namer work hit this.

A rebuild is for missing function starts, because `sync apply` does not create functions (spec/56-workflow-both-machines.md, assumption 3). `sync check` compares only `(address, kind)` pairs and names. A rebuild sets no sizes from `config/symbols.txt`, because Ghidra computes them. So a rebuild cannot fix a size-only change.

## Decision

1. The `functions` hash covers only the address and kind columns of each `function` line, in file order, each pair followed by a newline. It equals `awk -F'\t' '$2 == "function" {print $1 "\t" $2}' config/symbols.txt | sha256sum`. The stamp key stays `functions`.
2. When the `functions` hash differs, the hook prints `ghidra project: function starts changed, run tools/rebuild-ghidra.sh, then sync apply and sync check`.
3. A rename, a tier or evidence change, or a size-only change of a function changes only the `symbols` hash. The hook prints `ghidra project: names changed, run sync apply and sync check`.

Out of scope: a size check in `sync check`, any change to `sync apply`, and the `symbols` hash.

## Consequences

- A namer task asks for `sync apply` and `sync check`, not for a rebuild.
- Stamps written before this change hold the old hash. Each machine prints `function starts changed` once, and the rebuild steps write a new stamp.
