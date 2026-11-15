# ADR-0001: A byte-matching decomp with the GameCube decomp as donor

- **Status:** Accepted (user decision)
- **Date:** 2026-10-10

## Context

The goal is C++ source for the Xbox release of The Sims Bustin' Out that rebuilds `default.xbe`. A matching decomp of the GameCube release (daftblazer/bustin-out-decomp) exists and moves fast. xboxrecomp can statically recompile an XBE. decomp.me offers a web UI for matching that the user does not need.

## Decision

Functions are matched byte for byte with the original compiler (ADR-0004), first function by function and grouped into source files later. The GameCube decomp is a donor of names, types and draft C++; its names enter `symbols.txt` as the `gc` tier with two independent kinds of evidence. The recomp is only a phase 2 harness for running rebuilt code. decomp.me is not used; matching runs locally.

## Consequences

- Progress is measured in matched bytes of game code, with SDK code excluded.
- A GameCube name is a strong hint, confirmed in the Xbox code through ghidra-mcp before use. GameCube types are checked against the field offsets the Xbox code uses, because GCC 2.95 and MSVC 7.1 lay out classes differently.
- GameCube compiler idioms (GCC 2.95 trailing branches) do not transfer; method lessons may (docs/gc-donor-watch.md).
