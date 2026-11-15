# ADR-0005: SDK names come from byte matches against the libraries the XBE stamps

- **Status:** Accepted
- **Date:** 2026-10-10

## Context

Much of `.text` is XDK library code, which is never decompiled. Ghidra's Function ID guesses among equal library functions (F-0004), and matching against every XDK library produced false matches (F-0002).

## Decision

`bodecomp/libmatch.py` compares each Ghidra function's bytes with every function in the libraries stamped in the XBE (XAPILIB, XBOXKRNL, LIBCPMT, LIBCMT, D3D8, XGRAPHC, DSOUND, XMV), skipping bytes at relocation sites. Inside the SDK address ranges an ambiguous match is recorded as `lib-ambiguous(<count>):<first five names>`. Outside them only a unique match names a function (F-0003).

## Consequences

- 2,007 functions are named, 431 are ambiguous and 71 are named only by section (docs/LEDGER.md).
- Rerunning libmatch is idempotent (F-0012).
- SDK functions are linked from the original `.lib` files in the final build.
