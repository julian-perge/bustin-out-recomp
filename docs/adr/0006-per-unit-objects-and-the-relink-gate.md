# ADR-0006: Per-unit target objects, and the re-link check as a gate

- **Status:** Accepted
- **Date:** 2026-10-10

## Context

Matching compares each compiled function with a target object cut from the original `.text`. The delinker drops PC-relative relocations inside one exported range (F-0007) and names calls to thunks after their targets (F-0008).

## Decision

`tools/delink.sh` cuts each unit, from one function start to the next, into its own COFF object. A headless Ghidra run turns every thunk into an ordinary function in memory, exports `.text` as one object, and writes the delinker's relocations and the symbol it would name at each address (`ExportDelinkTables.java`). `uv run python -m bodecomp.unitsplit` then builds each unit object from those tables the way the delinker's COFF exporter would. `uv run python -m bodecomp.relink` places every unit object at its address, applies its relocations and compares the result with `.text`. Zero mismatched bytes, zero unresolved names and zero unit problems is the gate for any change to symbols, units or the export scripts.

## Consequences

- An export needs the ghidra-mcp server stopped. Exporting each unit from Ghidra took about 85 minutes for the 19,784 units of M2a, because the exporter scans every symbol and relocation in the program for each unit. The Python split takes seconds.
- The Python split copies the exporter's rules: it trims PC-relative relocations whose instruction only refers inside the unit, leaves relocations narrower than four bytes unpatched and unemitted, and lists every named target outside the unit as an undefined external. `ExportUnits.java` stays as the reference: after a delinker update, export the units with it and run `uv run python -m bodecomp.unitsplit --compare <folder>`, which must report 0 objects differ.
- On 2026-10-11 the Python split of the 19,794 M2b units matched `ExportUnits.java` on every unit (sections, relocations and symbols, compared after parsing) and passed the re-link gate with 0, 0 and 0.
- Code in gaps outside Ghidra functions rides along with the preceding unit until it gets units of its own (F-0016; since M2a, F-0026).
