# M3 results

M3 is one matcher batch merged through the full gate, with its lessons folded into the agent prompts. The user approved the plan's relocation rule and asked for functions with 1 to 3 relocations (2026-10-12). After batch 1, the user ruled that a function whose source uses placeholder names keeps its `auto` name (ADR-0011) and asked for a second batch covering the relocation kinds batch 1 never used.

## Tools

- `bodecomp.match` compiles every `src/**/*.cpp` with VC71 at `/O2 /G7 /arch:SSE`, compares each function with its delinked target unit under the relocation rule (docs/WORKFLOW.md, "Matching"), and writes `config/functions.csv`.
- `bodecomp.match candidates N` lists unmatched game functions by relocation count and size.
- `names set` with a `src/` path refuses a function that `config/functions.csv` does not list as `matched` from that file.
- `docs/LEDGER.md` has a table of game functions by match status, read from `config/functions.csv`.

## Batch 1: 15 functions, all matched

- Picked with `match candidates 100000 --min-size 24 --min-relocs 1`, the first five each with 1, 2 and 3 relocations: 0x00011400, 0x00018390, 0x00027EF0, 0x00032E50, 0x00049070, 0x00050620, 0x00058000, 0x000C1900, 0x000C1A20, 0x000C1A80, 0x000C1B10, 0x000C1B50, 0x00125CC0, 0x00125EF0, 0x00125F10. All are 24 bytes.
- The relocations were calls to `FUN_` functions and references to `DAT_` globals and function pointers only.
- Idioms: callees are members named `FUN_xxxxxxxx` on stand-in structs `S_<address>` so that thiscall setup comes out right; globals are `extern` `DAT_xxxxxxxx`. 0x00050620 needs a temporary to get the store order (F-0070). 0x00058000 declares 21 placeholder virtuals to reach slot 20 (F-0071).
- A match proves that addresses agree, not that declared types or classes are right (F-0069).

## Batch 2: 6 functions, 5 matched and 1 parked

Picked by hand, one per relocation kind batch 1 never used, and checked in Ghidra first.

| Kind | Function | Result |
|---|---|---|
| vtable emitted by the compiler | 0x0001BC70 | matched |
| float literal | 0x00048D70 | matched |
| callee resolved by its real name (`LoadSignStrings`) | 0x0006BA00 | matched |
| string literal | 0x00163790 | matched |
| callee in the same file | 0x000FAE60 | matched |
| caller of a callee in the same file | 0x000FAED0 | parked, 7.7, `unclassified` |

- The first four kinds match without special handling (F-0072).
- VC71 at `/O2` inlines 0x000FAE60 into 0x000FAED0, while the target keeps the call, so the resolver's same-file call path is still untested on real code (F-0073). The design spec's blocker classes have no `inlining` class.
- After M3 (2026-10-12): moving 0x000FAED0 to its own file, with the placeholders renamed to `FUN_000FAE60` and `FUN_000FAED0`, matched it at 100 (F-0073 confirmed). `match --check` then reports 21 matched, 0 parked.
- A first pick for the same-file call, 0x0003B2F0, was dropped: it is a compiler-generated adjustor thunk (`sub ecx,[ecx-4]; jmp 0x0003B300`).

## Gate

On `m3-first-batch` after both merges: `bodecomp.match --check` reports 20 matched, 0 nonmatching, 1 parked, 0 error; `pytest` 196 passed; `ruff check` clean; `sync check` 0 differences; `names check` 0 problems; `ledger --check` and `findings check` clean. No `names set` was run: every matched source uses placeholder names. The ledger counts 20 matched game functions (410 bytes) and 1 parked.

## Lessons for the agents

- Matcher: placeholder names are fine; a callee with a non-`auto` name in `config/symbols.txt` is called by that name. Count a function's stack arguments from its `ret N`, not from Ghidra's signature. Declaring virtuals named `FUN_xxxxxxxx` in slot order makes the compiler emit a matching vtable. A callee defined in the same file may be inlined; put the caller in its own file, with `FUN_XXXXXXXX` placeholder names (F-0073).
- Reviewer: read every constant a match depends on from Ghidra instead of inferring it from the match. Search docs/FINDINGS.md for an address in its `0x%08X` form.
- Lead: disassemble a hand-picked candidate before giving it out; compiler-generated thunks look like ordinary small functions in `match candidates`.
