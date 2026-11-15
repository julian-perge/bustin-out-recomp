# M1 results

M1 meets all four of its exit conditions. The Ghidra project rebuilds from the XBE and `config/symbols.txt`. SDK functions are named from the XDK libraries. Re-linking the per-function target objects reproduces `.text` byte for byte. The preliminary raw-search findings are re-checked in Ghidra.

The work is on branch `m1-analysis`. Decisions made along the way were recorded as ADRs and findings (ADR-0007), for example ADR-0005 and ADR-0006.

## SDK names from the XDK libraries

`bodecomp/libmatch.py` compares each Ghidra function's bytes with every function in the XDK 5558.2 `.lib` files, skipping bytes at relocation sites. It uses only the eight libraries stamped in the XBE (XAPILIB, XBOXKRNL, LIBCPMT, LIBCMT, D3D8, XGRAPHC, DSOUND, XMV). Matching every `.lib` in the XDK claimed short game functions as `dmusic.lib` code, and the game never linked that library.

| Result | Count |
|---|---|
| Library functions read | 11,630 |
| Named from a unique match | 2,007 |
| Ambiguous (several library functions with the same bytes) | 431 |
| Named only by their SDK section | 71 |

All 431 ambiguous matches are inside the SDK address ranges. Their evidence lists the first five candidate names and the total count, for example `lib-ambiguous(4):_OpenEventA@12,...`. 219 of them have more than five candidates, at most 127. Outside those ranges only a unique match counts, because 16 to 18 byte generic functions matched unrelated classes in several libraries. Two unique C runtime matches sit just below the second SDK block: `__cfltcvt_init` at 0x0021DEA4 and `__fpmath` at 0x0021DEEC.

I spot-checked five names against their callers and callees in Ghidra, and each fits:

- 0x00290BAB `??_GCDirectSoundStreamSettings` calls a destructor and `MemFree`.
- 0x002B244C `_XMVDecoder_Play@12` calls D3D device overlay functions.
- 0x0026BCDC `?ComputeEffectiveSwizzles@XGRAPHICS` is called by `MergeSwizzles`.
- 0x00243F70 `?GetRefreshRate@CMiniport@D3D`.
- 0x00299747 `?ds_alog`.

`config/symbols.txt` now has 10,384 entries: 2,617 SDK functions, 7,558 functions with Ghidra's automatic names, and 209 SDK data labels. 109 names carry their own address as a suffix to stay unique. 76 of them are thunks with automatic names, which Ghidra would otherwise show under their shared target's name. The other 33 are SDK-tier names that appear more than once, such as the XBE header labels. Five of those 33 are `thunk_` names too.

## Delinking `.text`

`tools/delink.sh` runs the ghidra-delinker-extension headlessly.

- The whole-section object `build/target/text.obj` is 2,305,252 bytes (0x232CE4) with 27,552 relocations: 27,256 DIR32 and 296 REL32.
- The delinker drops a PC-relative relocation when its target is inside the exported range. So calls between functions inside one whole-section object have their offsets baked in. To keep those relocations, each unit is exported as its own object: 8,271 objects, written in about 26 minutes, with none failing.
- The delinker names a call to a thunk after the thunk's target. The export scripts therefore turn every thunk into an ordinary function, in memory only, before exporting.

## Re-link check

`uv run python -m bodecomp.relink` places every unit object at its address, applies its relocations, and compares the result with `.text` from the XBE.

| Result | Value |
|---|---|
| Units | 8,271 |
| Bytes covered | 2,305,252, equal to the `.text` size |
| Relocations applied | 56,858 |
| Mismatched bytes | 0 |
| Unresolved names | 0 |

The command also requires one object for each span in `build/target/units.txt`, with the same length, and counts any byte that no unit wrote, or that two units wrote, as a mismatch. It reports 0 unit problems. As a control, flipping one byte in the reference image produces exactly one mismatch.

Getting to zero took four fixes:

- Names are looked up without their Ghidra namespace (`D3D8::`).
- Imports resolve to their `thunk_` stub in `.text`.
- The sync also exports labels that live in namespaces.
- Thunks are exported as plain functions.

## Rebuilding the Ghidra project from text

`tools/rebuild-ghidra.sh` deletes the project, imports `orig/default.xbe` with the XBE loader, and analyzes it. This takes about two minutes and finds 10,311 functions, the same count as the M0 project. Then `sync apply` renamed 1,988 functions and labels, `sync check` reported 0 differences, 0 entries missing in Ghidra and 0 Ghidra entries missing from `symbols.txt`, and a following `sync export` renamed nothing and left `symbols.txt` unchanged.

The first rebuild failed the check, and `sync apply` changed in two ways to fix it:

- A thunk with no name of its own shows `thunk_FUN_...` while its target has a default name, and the target's name once the target is named. Naming a target could therefore change a thunk name that had already matched. `apply` now repeats until no renames remain.
- Ghidra lists a label only when it sits on defined data. Three XAPILIB globals were on untyped bytes, and their Task 7 types lived only in the old project. `apply` now defines a one-byte `undefined1` at any data entry it cannot see before naming it. It never clears what is already there: if the address holds code or data, Ghidra refuses and `apply` stops with that error.

## Function coverage: cross-check with the xboxrecomp disassembler

| Set | Function starts in `.text` |
|---|---|
| Ghidra | 8,270 |
| xboxrecomp | 16,771 |
| Both | 7,862 |
| Ghidra only | 408 |
| xboxrecomp only | 8,909 |

Ghidra's 8,270 functions cover 1,636,344 bytes. The remaining 668,908 bytes (29% of `.text`) are outside every Ghidra function, in 7,982 gaps found by ghidra-mcp `find_code_gaps`. 1,092 of those gaps, 376,286 bytes in total, contain instructions that belong to no function. The largest is 56,697 bytes right after `_CancelIo@4` (0x00232D07 to 0x00240A7F).

Almost all of the xboxrecomp-only starts are in those gaps:

| Where the xboxrecomp-only start is | How xboxrecomp found it | Count |
|---|---|---|
| In a gap | after `int3` padding | 8,558 |
| In a gap | call target | 288 |
| In a gap | tail-jump target | 58 |
| In a gap | prologue | 2 |
| Inside a Ghidra function | tail-jump target | 3 |

This does not affect the re-link check, because each unit runs from one function start to the next and takes the gap bytes with it. It does matter for M2: the gaps hide functions that need their own units before they can be matched. The 288 call targets are the first ones to look at.

## Preliminary findings, re-checked in Ghidra

- RTTI type names are confirmed absent. ghidra-mcp `search_strings` finds no `.?AV` or `.?AU` string. A byte search of all program memory (`search_byte_patterns` for `2E3F4156` and `2E3F4155`) finds none either. A control search for `.\e_graphics.cpp` does find its string. Class names will not come from RTTI.
- The `.cpp` count is corrected from 16 to 15. `search_strings` finds 14 defined strings, such as `.\Neighborhood.cpp`, `.\IFFResFile2.cpp`, `.\ObjectModule.cpp` and `.\e_graphics.cpp`. A byte search for `.cpp` finds one more, `.\aptauxpceorgl.cpp` at 0x002EB38C, which Ghidra had not defined as a string. The raw search's sixteenth hit was not in loaded memory; I did not track down where it came from. The nine `c:\eor\src2\...` header paths are confirmed.
- Apt is confirmed in the Xbox build. Ghidra lists no references to the Apt string, because its bytes are undefined. A byte search for its address finds the code at 0x000FBC18. It pushes `"Flash animation"`, `0x780` (line 1920), `".\aptauxpceorgl.cpp"` and `0x100`, which is an allocation call that passes its source file and line. The strings next to it are `PCGL geometry file`, `.geo` and `Flash animation`. That code is in the gap 0x000FB4E1 to 0x000FC0FF after `FUN_000FB330`, so Ghidra has not made it part of any function. The GameCube decomp's Apt work (`include/ui/Apt.h` and its matched functions) is a donor for this code.
