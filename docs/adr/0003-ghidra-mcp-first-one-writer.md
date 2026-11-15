# ADR-0003: ghidra-mcp first for analysis, one writer at a time

- **Status:** Accepted (user decision)
- **Date:** 2026-10-10

## Context

Raw byte and string searches of the binary match bytes that are not code or data references, which produced false findings before the Ghidra project existed (F-0019). ghidra-mcp's server holds one shared program in memory, and 103 of its 205 tools change it.

## Decision

Questions about functions, references, strings, types and call graphs are answered through ghidra-mcp against the project. A raw search result is labelled preliminary until Ghidra confirms it. One session or agent writes to the Ghidra project at a time: the lead session or a single `namer`, recorded as owner in `docs/STATUS.md`. The `matcher` and `reviewer` agents get only the read-only tools (ADR-0007).

## Consequences

- The server has to be running for analysis (`tools/ghidra-mcp-headless.sh`).
- Headless jobs that open the project, such as the delink and the rebuild, need the server stopped first, because both hold the project lock.
- A reader has no ghidra-mcp write tools, but its Bash can still write through `uv run python -m bodecomp.sync apply` or the server's HTTP API. Its instructions forbid both; nothing enforces it (F-0025).
