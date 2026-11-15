# ADR-0008: String-tier names are recorded in text first, with string addresses as evidence

- **Status:** Accepted
- **Date:** 2026-10-11

## Context

M2b names game functions from the strings they reference (the design spec's `string` tier). Ghidra holds no tier or evidence, so a name given in Ghidra and exported became an `sdk` name with `xbe-loader` evidence. The sync cannot create Ghidra namespaces: renaming a function to `A::B` through ghidra-mcp keeps it in the global namespace under the literal name, and `find_functions` reports only a function's own name.

## Decision

- A string name is written to `config/symbols.txt` with `uv run python -m bodecomp.names set` and pushed with `sync apply`. `sync export` stops when a function is named in Ghidra but `auto` in `symbols.txt`; `--accept-ghidra-names` takes such names as SDK names, as before.
- Evidence is `stated:` or `string:` followed by the addresses of strings the function references. `stated:` is written by `names stated` when a string states `Class::Method()`, that name is stated in no other function, and the function's strings state no other name. `string:` is a namer's judgment. `names check` confirms each cited address against `build/strings.tsv`.
- A name is `Class::Method` when a string the function references states the function is a member of the class, and a flat CamelCase name otherwise. A class's name on its own, or an allocation tagged "X operator new", says which class the function works with, not which class it belongs to (F-0033), so it gives a flat name such as `RegisterESimClass` or `CreateERRleTexture`. `Class::Method` is stored as a literal name; real namespaces come with types.

## Consequences

- A reviewer checks each namer batch against Ghidra before it is committed.
- `build/strings.tsv` must be exported again (`tools/export-strings.sh`) after functions change, before `names check`.
- Literal `A::B` names reach the delinked objects as they are; the re-link resolves them by exact name first.
