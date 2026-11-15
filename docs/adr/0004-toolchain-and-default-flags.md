# ADR-0004: XDK 5558.2 VC71 under wibo, default /O2 /G7 /arch:SSE

- **Status:** Accepted (M0 passed 2026-10-10); the default flags are amended by ADR-0017
- **Date:** 2026-10-10

## Context

The XBE was built with XDK 5558. The user's XDK 5558.2 archive contains `CL.Exe` 13.10.3077. M0 compiled 20 hand-written functions under a matrix of flag sets (docs/m0-results.md).

## Decision

The compiler is XDK 5558.2 VC71 (`CL.Exe` 13.10.3077) run under wibo 1.2.0 on macOS. The project default is `/O2 /G7 /arch:SSE`, which matched 19 of 20.

## Consequences

- `/arch:SSE`, `/G7` and frame-pointer omission are required (F-0022).
- `/Ox` matches the same 19, so `/O2` against `/Ox` stays open (F-0018). Keep both in any flag matrix.
- A library may have been built with other flags; the GameCube build compiles Apt at -O0 (F-0021). A per-library exception needs its own evidence and an ADR that supersedes this one for that library.
