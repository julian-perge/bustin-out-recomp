# Findings

Facts about the binary, the tools and the GameCube donor, one entry each. Search here with `rg` before investigating an address, a function or a tool's behavior; `rg -n '0x000FBC18' docs/FINDINGS.md` finds every entry that names that address. A settled entry (confirmed, fixed or rejected) is cited, not redone. Reopen one only with new evidence, and write the new evidence into the entry. Decisions about method are in `docs/adr/`, not here.

Format: a `## F-NNNN <title>` heading, then a `- Status:` line with one of `open`, `active (<owner>, <YYYY-MM-DD>)`, `confirmed`, `fixed (<commit>)` or `rejected`, then Addresses (as `0x%08X`), Checked (`ghidra-mcp (<date>)`, `test <name>`, `relink run`, `GC repo <sha>` or `preliminary (raw search)`), Evidence, and either Next (open entries) or Revisit when (settled entries). IDs are never reused. Entries stay short; long write-ups go in `docs/topics/` and are linked. `uv run python -m bodecomp.findings check` checks the format. A `fixed` entry from before the first public commit cites a commit of the private history, and `config/pre-public-commits.txt` lists those hashes (ADR-0016). Only the lead session edits this file; subagents propose entries in their reports.

## F-0001 Library functions were cut short at their own local labels
- Status: fixed (a373340)
- Checked: test test_labels_inside_a_function_do_not_end_it
- Evidence: `coff.function_bytes` ended a function at any symbol; library objects carry local labels inside function bodies, so `CloseHandle` came out 7 bytes instead of 30. It now ends a function only at the next function symbol.
- Revisit when: a library function's extracted length differs from its symbol size.

## F-0002 Matching every XDK library named game functions as dmusic.lib code
- Status: fixed (a373340)
- Checked: test test_only_the_libraries_the_xbe_links_are_used
- Evidence: matching all 54 `.lib` files claimed 16 to 18 byte game functions for `dmusic.lib`, which the game never linked. libmatch now uses only the eight libraries stamped in the XBE (ADR-0005); docs/m1-results.md.
- Revisit when: the XBE stamps a library that `libs_for_stamps` does not know (it raises an error).

## F-0003 Short generic functions match unrelated library classes outside the SDK ranges
- Status: fixed (a373340)
- Addresses: 0x0021DEA4, 0x0021DEEC
- Checked: test test_ambiguous_match_outside_sdk_is_not_claimed
- Evidence: outside the SDK address ranges only a unique match counts. The two unique C runtime matches there are real: `__cfltcvt_init` at 0x0021DEA4 and `__fpmath` at 0x0021DEEC, just below the second SDK block. docs/m1-results.md.
- Revisit when: a game function gets an `sdk` name from a match shorter than 20 bytes.

## F-0004 Names from Ghidra's own Function ID are not SDK evidence
- Status: fixed (eea0dee)
- Checked: test test_auto_names
- Evidence: Function ID marks a guess among equal library functions with `FID_conflict:` and leaves labels such as `__set_errno` on functions. The sync treats `FID_conflict:` names as automatic, the two entries that had them are labelled `ghidra-fid`, and `ghidra_api.rename` removes a same-named secondary label before renaming (a373340).
- Revisit when: a rename fails with "name already exists" at the same address.

## F-0005 A thunk with no name of its own displays its target's name
- Status: fixed (9c8acd4)
- Checked: test test_duplicated_auto_names_all_get_their_own_suffix, test test_thunks_to_named_functions_get_their_own_name
- Evidence: renaming one thunk renamed the others pointing at the same target, and kernel-import thunks collided with the imports in delinked objects. Every copy of a duplicated automatic name gets its own address suffix (1036347), and a thunk to a named function is named `thunk_<name>` (9c8acd4).
- Revisit when: `sync check` reports a thunk name difference.

## F-0006 Thunk renames need repeated passes to settle
- Status: fixed (99f1ccd)
- Addresses: 0x00292D54, 0x002DDB2D
- Checked: test test_apply_repeats_until_thunk_names_settle
- Evidence: naming a target changes the name its unnamed thunk displays, so a thunk that already matched could change again. `sync apply` repeats renames, at most five passes, until none remain. docs/m1-results.md (rebuild).
- Revisit when: `sync apply` stops after five passes with renames left.

## F-0007 The delinker drops PC-relative relocations whose target is inside the exported range
- Status: confirmed
- Checked: relink run
- Evidence: `TrimSuperfluousRelativePC` in the delinker's `CoffRelocatableObjectExporter.java:429`. A whole-`.text` object therefore has call offsets baked in. Worked around by exporting each unit as its own object (bd6aec8, ADR-0006). v0.9.3 was checked on 2026-11-14: its whole-`.text` object has 33,857 relocations, the same count as the v0.9.2 object, against 129,203 in `relocs.tsv`, so the workaround stays (F-0084).
- Revisit when: the delinker extension is updated past v0.9.3.

## F-0008 The delinker names a call to a thunk after the thunk's target
- Status: fixed (b8c3e36)
- Checked: relink run
- Evidence: all 1,166 remaining mismatch runs were calls whose real target is a thunk. Both export scripts turn every thunk into an ordinary function, in memory only, before exporting (`tools/ghidra_scripts/ExportUnits.java`).
- Revisit when: relink mismatches return at call sites.

## F-0009 Delinked names carry Ghidra namespaces, and imports appear under their library
- Status: fixed (b8c3e36)
- Checked: test test_resolve_falls_back_to_the_name_without_its_namespace, test test_an_import_resolves_to_its_thunk_in_text
- Evidence: names arrive as `D3D8::...`; relink falls back to the name after the last `::`, and a library-qualified import resolves to its `thunk_<name>` stub in `.text`.
- Revisit when: relink reports unresolved names.

## F-0010 Ghidra lists a label only on defined data, and list_globals skips namespaces
- Status: fixed (99f1ccd)
- Addresses: 0x0035B75C, 0x0035B760, 0x002D9D10, 0x002D9DC0
- Checked: test test_parse_data_item, test test_apply_defines_data_it_cannot_see_before_naming_it
- Evidence: the sync reads labels through `list_program_items` with `data_items` (b8c3e36), and `apply` defines a one-byte `undefined1` at a data entry Ghidra cannot see before naming it. The XAPILIB globals above were on untyped bytes. 0x002D9DC0 (`g_DeviceType_MU`) surfaced in M2a as an unresolved name in the re-link once the code that references it became a function, and was added to `symbols.txt` by hand; ghidra-mcp has no tool that lists labels on untyped bytes. In the M2a rerun, `sync export` on a rebuilt project before `sync apply` dropped all four of these entries, because export kept only entries that Ghidra lists; it now keeps named data entries that Ghidra does not list (test test_merge_keeps_a_named_data_entry_ghidra_does_not_list).
- Revisit when: `sync check` reports data entries missing in Ghidra.

## F-0011 ghidra-mcp apply_data_type clears the range unless told not to
- Status: fixed (eea0dee)
- Checked: ghidra-mcp source and the 2026-10-10 rebuild; no test pins the flag (`bodecomp/ghidra_api.py:110`)
- Evidence: `clear_existing` defaults to true (ghidra-mcp `DataTypeService.java:994,1111`), so defining a missing global could delete code or data. The sync sends `clear_existing: false`, and a conflict stops with Ghidra's error.
- Revisit when: ghidra-mcp is updated past 7.0.0.

## F-0012 Rerunning libmatch renamed entries whose names carry an address suffix
- Status: fixed (eea0dee)
- Checked: test test_running_again_keeps_a_name_made_unique_by_its_address
- Evidence: a rerun renamed 9 suffixed entries. It now keeps `lib:` evidence on entries it already named, and a second rerun leaves `symbols.txt` byte for byte identical.
- Revisit when: a libmatch rerun changes `symbols.txt` without new libraries.

## F-0013 There are no RTTI class names in the XBE
- Status: confirmed
- Checked: ghidra-mcp (2026-10-10)
- Evidence: `search_strings` finds no `.?AV` or `.?AU`, a byte search of all memory finds neither, and a control search for `.\e_graphics.cpp` works. Class names will not come from RTTI. docs/m1-results.md.
- Revisit when: never for this build.

## F-0014 There are 15 .cpp source names, not 16
- Status: confirmed
- Addresses: 0x002EB38C
- Checked: ghidra-mcp (2026-10-10)
- Evidence: 14 defined strings plus `.\aptauxpceorgl.cpp` at 0x002EB38C, which Ghidra had not defined. The nine `c:\eor\src2\...` header paths are confirmed. docs/m1-results.md.
- Revisit when: never for this build; F-0019 tracks the unexplained raw hit.

## F-0015 Apt, EA's Flash UI player, is in the Xbox build
- Status: confirmed
- Addresses: 0x000FBC18, 0x000FB4E1
- Checked: ghidra-mcp (2026-10-10)
- Evidence: the code at 0x000FBC18 pushes `"Flash animation"`, line 1920 and `".\aptauxpceorgl.cpp"` for an allocation call. Since M2a it is inside `FUN_000fbbb0` (0x000FBBB0, 205 bytes); before that it sat in the gap 0x000FB4E1 to 0x000FC0FF, outside any function (F-0016). The GameCube decomp's Apt work is a donor for it.
- Revisit when: never; the code location changes only if units change.

## F-0016 29% of .text is outside every Ghidra function
- Status: fixed (99e9ad3)
- Addresses: 0x00232D07
- Checked: test (uv run python -m bodecomp.gaps report, 2026-10-11)
- Evidence: 668,908 bytes in 7,982 gaps (`find_code_gaps`); 1,092 gaps hold 376,286 bytes of instructions that belong to no function. The largest is 0x00232D07 to 0x00240A7F after `_CancelIo@4`. 8,906 of xboxrecomp's 8,909 extra function starts are in gaps, 288 of them call targets. docs/m1-results.md (function coverage). M2a created functions at padding boundaries: the non-padding bytes outside functions fell from 510,274 to 115,169, and 16,694 of xboxrecomp's 16,771 starts are now functions. docs/m2-results.md.
- Next: none; the remaining gap code and the 13 rejected starts are tracked in F-0026.

## F-0017 0x00152660 matches under no flag set
- Status: open
- Addresses: 0x00152660
- Checked: test (M0 flag matrix, `uv run python -m bodecomp.m0`)
- Evidence: it writes a vector to a stream through three virtual calls. The best attempt has the right size (117 bytes) and identical bytes up to +0x47, where the compiler orders two stack slots differently. Parked after five attempts as a lifetime tie. docs/m0-results.md.
- Next: retry once more classes around it are matched; the cause is most likely the source shape.

## F-0018 Whether the game was built with /O2 or /Ox is unsettled
- Status: open
- Addresses: 0x000CFE30, 0x001CD490
- Checked: test (M0 flag matrix)
- Evidence: all 20 M0 functions compile the same under both. The only hint is weak: `$Object` has two copies, referenced from 0x000CFE30 and 0x001CD490, which `/GF` (part of `/O2`) would normally merge. Default stays `/O2 /G7 /arch:SSE` (ADR-0004). docs/m0-results.md.
- Next: decide when more game strings or the phase 3 file layout give evidence.

## F-0019 The raw search's sixteenth .cpp hit is unexplained
- Status: open
- Checked: preliminary (raw search)
- Evidence: the hit was not in loaded memory, and it was not tracked down. docs/m1-results.md.
- Next: look only if phase 3 needs every source-file name.

## F-0020 sync apply can count a thunk renamed in two passes twice
- Status: open
- Checked: test test_apply_repeats_until_thunk_names_settle
- Evidence: the "renamed" count printed by `sync apply` adds up renames per pass, so a thunk renamed in two passes counts twice. Names are unaffected; only the printed count is high. Left alone in the M1 review.
- Next: fix only if the count is used for something.

## F-0021 The GameCube build compiles Apt at -O0, so the Xbox Apt flags may differ
- Status: open
- Checked: GC repo d8483a60
- Evidence: daftblazer/bustin-out-decomp builds its Apt library at -O0 while the game uses -O2 (`configure.py`, commit 90d9b481). Nothing about the Xbox Apt flags has been checked: preliminary for Xbox. docs/gc-donor-watch.md (2026-10-11).
- Next: when Apt functions are matched, try other flags if they fail at the ADR-0004 default.

## F-0022 VC71 needs /arch:SSE, /G7 and frame-pointer omission to match
- Status: confirmed
- Addresses: 0x000D20E0, 0x0004A920
- Checked: test (M0 flag matrix)
- Evidence: without `/arch:SSE` 0x000D20E0 loses its `MOVSS` copies; with `/G6` or no CPU flag 9 more functions fail, including 0x0004A920 (`ADD [mem], 1`); with `/Oy-` 13 more fail. docs/m0-results.md, which also lists the source shapes that changed code generation in M0.
- Revisit when: a later batch finds a function that matches only without one of these flags.

## F-0023 Tool groups loaded after a subagent starts never reach it
- Status: open
- Checked: live subagent run (2026-10-11)
- Evidence: with the bridge's default lazy loading only the `listing`, `function` and `program` groups load on connect. A matcher that called `load_tool_group("xref")` got "No such tool available" for `get_xrefs_to`, while the tool appeared in the main session. `.mcp.json` passes `--no-lazy` since 8c44f56. Reopened in M2b batch 1 (2026-10-11): with `--no-lazy`, a namer found `get_xrefs_to` listed as not loaded, and `load_tool_group("xref")` did not make it callable in that agent. After that call the xref tools appeared in the main session, and the next agent (the batch 1 reviewer) could call them. The session had started while the server was down; that `--no-lazy` registers only what the server lists at connect is a guess.
- Next: start the server before the session, or have the lead load the `xref` group before dispatching agents; check whether a session started with the server up has the xref tools at once.
## F-0024 The headless ghidra-mcp server opens no program
- Status: confirmed
- Checked: live subagent run (2026-10-11)
- Evidence: `list_open_programs` returns an empty list after `tools/ghidra-mcp-headless.sh`, and calls without `program=` fail with "No program loaded" until a program is opened. Passing `program="default.xbe"` works, and `POST /open_program` with `{"path": "/default.xbe", "auto_analyze": false}` opens it for calls without `program=` such as `bodecomp.sync` (docs/WORKFLOW.md).
- Revisit when: the headless launcher starts opening the program itself.

## F-0025 Reader agents can still write to Ghidra through Bash
- Status: open
- Checked: live subagent run (2026-10-11)
- Evidence: `matcher` and `reviewer` have no ghidra-mcp write tools, but their Bash can run `uv run python -m bodecomp.sync apply` (auto-allowed by the user's `Bash(uv *)` permission; it POSTs `/rename_function`) or call the HTTP API on port 8089. Their instructions forbid both; nothing enforces it. Reported by the reviewer agent and the final branch review. The M2b batch 5 reviewer sent one GET to the server to see whether it was up; it changed nothing, and it shows the rule is not enforced.
- Next: no enforcement during M2, where only the namer or the lead session touches Ghidra (user decision, 2026-10-11). The M3 plan adds a PreToolUse hook that, for `agent_type` matcher and reviewer only, denies `bodecomp.sync apply`, `tools/rebuild-ghidra.sh` and `tools/delink.sh`, before the first matcher batch runs.

## F-0026 115,169 non-padding bytes of .text are still outside functions after M2a
- Status: open
- Addresses: 0x0009C68A, 0x0001F4C0, 0x000C314A, 0x00242680, 0x000E3E00, 0x000DCCB0
- Checked: test (uv run python -m bodecomp.gaps report, 2026-10-11); ghidra-mcp (2026-10-11) for the three rejected starts named below
- Evidence: 18,854 gaps holding 273,871 bytes, of which 16,407 gaps are padding only. The largest by non-padding bytes are 0x0009C68A-0x0009EAB0 (9,240), 0x0001F4C0-0x00020EF0 (6,689) and 0x000C314A-0x000C4070 (3,861). 13 candidate starts were rejected by `tools/create-functions.sh` and are still outside functions (listed in docs/m2-results.md). 0x00242680 and 0x000E3E00 have a normal prologue and a DATA reference from a pointer table, and 0x000DCCB0 has a pointer-table reference with ordinary code from +6, so at least those are real. Where disassembly fails, from a rerun on the 13: 0x00075200 at 0x000754EF, 0x000E10C0 at 0x000E10EF, 0x000E3DC0 at 0x000E3DF3, 0x000E3E00 at 0x000E3E33, 0x000E4C50 at 0x000E4C6F, 0x00158140 at 0x0015830F, 0x00193210 at 0x00193217, 0x001BEF10 at 0x001BEFD0, 0x00242310 at 0x0024231A, 0x00242680 at 0x00242682. 77 of xboxrecomp's starts are still not functions. The gap report approximates bodies that Ghidra splits into separate ranges, because `symbols.txt` holds only an address count. docs/m2-results.md.
- Next: look at what sits at each failure address and in the largest gaps with ghidra-mcp (`disassemble_bytes` with `dry_run`, `list_bookmarks`, `get_xrefs_to`).

## F-0027 Ghidra's analysis disassembles from constants that look like code addresses
- Status: confirmed
- Addresses: 0x00011100, 0x00011102, 0x00185410
- Checked: ghidra-mcp (2026-10-11)
- Evidence: `FUN_00185410` uses 0x00011102 as a constant six times; analysis treated it as an address and disassembled from it ("Found code from operand reference"), two bytes into the real function at 0x00011100. The project had 1,616 such bookmarks. Instructions like these conflict with disassembly from the real start, so `CreateFunctions.java` clears instructions outside functions and disassembles once more. docs/m2-results.md.
- Revisit when: never.

## F-0028 A 0xCC byte inside or at the end of an instruction looks like padding
- Status: confirmed
- Addresses: 0x001D9870, 0x001D9880, 0x00014AE0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x001D9880 follows a 0xCC that is the ModRM byte of `or ah,8` (`80 cc 08`) inside the function at 0x001D9870, and as a function it decodes as garbage. 0x00014AE0 follows `movaps xmm1,xmm4` (`0F 28 CC`), where the code continues. A raw-byte rule cannot tell these from padding; `CreateFunctions.java` rejects them as `mid-instruction` and `falls-through`. docs/m2-results.md.
- Revisit when: never.

## F-0029 GameCube names reach under 1% of Xbox game functions today, though string pairing is accurate
- Status: confirmed
- Addresses: 0x000CA090, 0x002420F0, 0x801853F0
- Checked: GC repo d8483a60, Ghidra headless (2026-10-11)
- Evidence: 271 Xbox game functions pair with GameCube functions on strings that one function references on each side; 130 of them also have a paired caller or callee. Only 13 of the GameCube partners have a full name, because daftblazer's `symbols.txt` names 517 of 10,870 functions (415 more carry only a class). Only 697 of 18,893 Xbox game functions reference any string. In a hand check of 20 pairs, 19 fit the same function and one is a static initializer: MSVC emits one per global (0x002420F0), GCC one per file (0x801853F0). Call-order propagation is unsettled (2 of 6 held-out anchors agreed). docs/m2-results.md.
- Revisit when: daftblazer's full names pass a few thousand functions, or a Sims 2 GameCube binary is available to test the Sims 2 map.

## F-0030 Strings of three characters or fewer are missing from build/strings.tsv
- Status: open
- Addresses: 0x00025A20, 0x002E2ED0, 0x002E2954, 0x0001B890, 0x0001B920, 0x0001B9B0, 0x0001BA40
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x00025A20 reads 0x002E2ED0, which holds "age" (61 67 65 00), and the four button functions pass 0x002E2954 to "setButtonContext". Neither address is in build/strings.tsv: `ExportStringRefs.java` takes undefined bytes as a string only from four characters up, and Ghidra has not defined these as strings. A namer cannot cite them.
- Next: decide whether to accept shorter undefined strings (more false strings from data) or define these in Ghidra, then export strings.tsv again.

## F-0031 Ten CAS field functions have no references in Ghidra
- Status: open
- Addresses: 0x00015070, 0x000254A0, 0x00025510, 0x00025A20, 0x00025A80, 0x00025B20, 0x00026030, 0x00026090, 0x00026100, 0x00026D00
- Checked: ghidra-mcp (2026-10-11)
- Evidence: `get_xrefs_to` finds no references to any of the ten. Neighbors of the same shape are referenced from vtables, for example the sign field at 0x002E2F30 and 0x002E2F34 (0x00026340, 0x00024E60). Whether these sit in vtables Ghidra has not defined, or are unused code, is not known.
- Next: search .rdata for each address as a pointer with `search_byte_patterns` (preliminary until Ghidra confirms), then define any vtable found or record them as unreferenced.

## F-0032 names set cannot record C++ operator names such as ERRleTexture::operator new
- Status: open
- Addresses: 0x00049EC0, 0x000FB0A0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x00049EC0 calls the allocator 0x122B90 with "c:\eor\src2\games\sims\esrc\e_rrletexture.h", line 0x2C, and "ERRleTexture operator new" (0x002E3BAC), and returns the result. It has no references (the F-0031 shape); the same allocation is inlined in 0x00049F60 and 0x0004A1C0. The NAME pattern in `bodecomp/names.py` accepts no `operator` form with a space or a symbol, so the stated name cannot be recorded.
  0x000FB0A0 has the same shape for "ERTexture operator new" (allocator 0x122B90, e_rtexture.h line 0x2A) and no references; the same allocation is inlined in LoadTgqTexture (0x000FC950).
- Evidence (batch 10): 0x001462B0 is one call to 0x00122B90 with the "ERAnim operator new" tag and e_ranim.h, so it waits for the same decision; the batch 10 namer had called it AllocERAnim and the reviewer cleared it. 0x0015FD10 and 0x00160510 ("ERSampleData operator new") wait too. CreateERAnim 0x00146350 keeps its name because it also constructs.
- Evidence (2026-10-12): the user chose the mangled spelling. Operator delete at 0x000136E0 was first recorded as `??3@YAXPAX@Z` with tier `sdk`, which was wrong (F-0081); it is now `matched` from src/game/auto/000136E0.cpp. `bodecomp.match` now reads `operator new` and `operator delete` definitions, free or in a class, so a matched source can name these functions; `MATCHED_NAME` in `bodecomp/names.py` already accepts mangled names, while `NAME` for the `string` tier still does not.
- Next: name 0x00049EC0 and 0x000FB0A0 as `??2ERRleTexture@@SAPAXI@Z` and the ERTexture equivalent, either by matching them from a source that defines `ERRleTexture::operator new` or by widening NAME in `bodecomp/names.py`.

## F-0033 An "X operator new" tag names the type allocated, not the class of the function
- Status: confirmed
- Addresses: 0x00049F60, 0x0004A1C0, 0x002E3BAC, 0x002E3BC8, 0x002E3BF8
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x00049F60 and 0x0004A1C0 both call the allocator 0x122B90 with size 0x3C, "e_rrletexture.h" line 0x2C and "ERRleTexture operator new", which is ERRleTexture's class operator new inlined. 0x00049F60 is slot 5 of vtable 0x2E3BC8, not of ERRleTexture's vtable 0x2E3BF8, and ignores its incoming ECX. 0x0004A1C0 installs vtable 0x2E3BF8 and is the create callback passed to 0x1550C0 (F-0034). The batch 2 reviewer renamed both from `ERRleTexture::` names to `CreateERRleTextureFromStream` and `CreateERRleTexture`; ADR-0008 now states the rule.
- Revisit when: types for ERRleTexture or its loader class are recovered.

## F-0034 0x1550C0 builds a class type record and 0x154FF0 registers it
- Status: confirmed
- Addresses: 0x001550C0, 0x00154FF0, 0x00049E70, 0x0004A260, 0x0005EDC0, 0x00060A40, 0x00066F20, 0x00240A10, 0x00240E60, 0x00240E90, 0x00240EC0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x1550C0 (thiscall, 94 callers) stores a create callback, two more callbacks, the class name, the name's hash (0x14C1A0), a 16-bit id and a parent record pointer, and counts records at 0x35E0E4. 0x154FF0 pushes the record onto the list at 0x35E0E4 and inserts it into a tree keyed by name hash at 0x35E0E0. Each class has an unreferenced out-of-line Register function that takes the id as an argument (for example RegisterESimClass, 0x00066F20) and a dynamic initializer in 0x2409C0..0x242B40 that usually passes 0 (F-0064) and stores the record pointer (0x240A10 stores to 0x310470). EIFenceWall's parent is 0x31071C, the EIWallPart2 record. The parent records give a hierarchy: ISimInstance (0x318BC8, parent 0x35E2D0) is the parent of ESim (0x310760) and ISimsObjectModel (0x318AF0), which is the parent of ISimsWallObjectModel (0x318B68), ISimsMultiTileObjectModel (0x318AC8), ISimsCounterTopObject (0x318B18) and IShrubObject (0x318B40); EIFloor (0x311548) has parent 0x35E1A0. Their dynamic initializers are 0x240FF0..0x241110.
- Revisit when: the record globals get names; the class-record initializers are named `DynamicInit_<X>Class` until then (batch 14, WORKFLOW), and take `DynamicInit_<Global>` names after.

## F-0035 Four body-type bone-scale functions need a rule for their qualifiers
- Status: open
- Addresses: 0x00028620, 0x00066980, 0x000C6FE0, 0x000D2D10
- Checked: ghidra-mcp (2026-10-11)
- Evidence: All four reference BoneScaleValues and the Heavy/Skinny A/C M/F strings (0x2E3134, 0x2E3128, 0x2E30FC). 0x28620 is installed by the SetupCasSim functions, 0x66980 by 0x692E0 ("Sim::Table", "*esim1*"), 0xC6FE0 by 0xC74B0, 0xC7680 and 0xC7770, and 0xD2D10 by 0xD31E0 and 0xD32C0. The callers of the last two reference no strings. Batch 1 and 2 named the first two ApplyBodyTypeBoneScales and ApplySimBodyTypeBoneScales.
- Next: decide how a qualifier is chosen (caller strings, owning vtable) before naming 0xC6FE0 and 0xD2D10.

## F-0036 Slot 12 of a shared base-class vtable returns the object's name
- Status: open
- Addresses: 0x00051EA0, 0x0008C920, 0x000B6960, 0x001C24D0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Vtables 0x2E3FF4, 0x2E6138 and 0x2E7FC8 share the base methods 0x1C24D0, 0x1C25F0 and 0x1C1EC0 in slots 3 to 5. Their slot 12 returns "Action Queue Manager", "Live Mode Game State" and "Server Responder". 17 vtables reference 0x1C24D0.
- Next: name the other slot-12 functions Get<X>Name, as batch 2 named 0x00051EA0 GetActionQueueManagerName.

## F-0037 The cheat codes appear to set the system.cnf variables
- Status: open
- Addresses: 0x00071BC0, 0x00034360, 0x000705C0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Preliminary, because nothing yet shows that ApplyCheatCode's `this` and the 0x705C0 owner are the same class. 0x705C0 calls RegisterSystemCnfVariables with an owner object whose variables sit at +0x13C onward (freeitems +0x13D, unlock_all_items +0x13F, unlock_party_motel +0x141, unlock_freeplay_mode +0x142, Cam_First_Per +0x148). ApplyCheatCode sets the same offsets on `this`: FREEALL +0x13D, MIDAS +0x13F, PARTY M +0x141, SIMS +0x142, FISH EYE +0x148.
- Next: find ApplyCheatCode's caller or vtable and confirm its `this` is the 0x705C0 owner class.

## F-0038 build/strings.tsv takes some 4-byte float constants for strings
- Status: confirmed
- Addresses: 0x002E5210, 0x002E53DC, 0x00078000, 0x00079870
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x2E5210 holds 33 33 73 3F 00 00 5C 42, which is 0.95f followed by 55.0f, and 0x00078000 uses both. 0x2E53DC holds 66 66 61 3F 00 00 6C 3F, which is 0.88046875f, the value 0x00079870 assigns. `ExportStringRefs.java` reads a float's four printable bytes and the 00 that starts the next float as the strings "33s?" and "ffa?", so `names batch` lists them. A namer can skip them; they do not support a name.
- Revisit when: the string export changes, for example to skip four-byte runs that the code reads as float operands.

## F-0039 The HouseSelect screen class has no stated name
- Status: open
- Addresses: 0x002E5728, 0x0007CE40, 0x0007CFB0, 0x0008EC70, 0x0007D490, 0x00078E30, 0x0007A260, 0x00078AE0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0x7CE40 (only caller 0x8EC70) installs vtable 0x2E5728, and the destructor 0x7CFB0 calls ShutdownHouseSelectScreen. Slot 1 is UpdateHouseSelectScreen, and slots 7 and 8 are SetHouseSelectVariable and GetHouseSelectVariable, the slots of SetCASVariable and GetCASVariable in the CAS vtable 0x2E24C0. No string states the class name. Batch 3's twelve flat HouseSelect names rest on the HouseSelect text table (GetHouseSelectString, 0x737F0) and the `hs_` variable prefix. Menu mode 0x310D68 values 0..5 select the menus at +0x100..+0x114; mode 4 (+0x110, items "quit" and "options") is the pause menu, so 0x78AE0 is SetPauseMenuItemText.
- Next: if a string or the GameCube donor states the class name, revisit the HouseSelect names.

## F-0040 0x000975FF is a branch target inside 0x000975F0, not a function start
- Status: fixed (660a645)
- Addresses: 0x000975F0, 0x000975FF, 0x002E6AA8
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0x975F0 (`push ebp; mov ebp,ecx; cmp [ebp+0x44],0; jnz 0x975FF; xor eax,eax; ret 4`) is slot 8 of the load-bar vtable 0x2E6A88 (referenced from 0x2E6AA8). 0x975FF is reached only by that jump; it holds the "current_load" compare and a sprintf of [ebp+0x48], and uses EBP without setting it. Ghidra split one function in two, so the strings sit on the fragment.
M2b Task 7 (2026-10-12) deleted both functions and created 0x975F0 again as one 109-byte function. The strings export then put "current_load" (0x2E6B10) on 0x975F0, which is named GetLoadBarVariable with that string as evidence.

## F-0041 Two near-identical menu classes are the buy menu (0x2E7110) and the build menu (0x2E6E38)
- Status: confirmed
- Addresses: 0x002E6E38, 0x002E7110, 0x0009F540, 0x000A1B00, 0x000A80B0, 0x0009ABB0, 0x000A0A30, 0x0009ADF0, 0x000A1910, 0x0009B270, 0x000A0B70, 0x0009B3C0, 0x000A0CA0, 0x0009B450, 0x000A06F0, 0x0009EAB0, 0x000A1C00, 0x0009F720
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0xA80B0 builds two members: 0x9F540 installs vtable 0x2E6E38 (class A) and 0xA1B00 installs vtable 0x2E7110 (class B). Both share base slots 3 to 5 (0x124700, 0x1458E0, 0x1458B0). Class A has slot 1 0x9EAB0, slot 2 0x9C6B0 and slot 6 0x9B450, with an item count in 0x319380; class B has slot 1 0xA1C00, slot 2 0x9F720 and slot 6 0xA06F0, with its count in 0x31938C. These pairs differ only in the count global: 0x9ABB0/0xA0A30 (updateInfoLozenges), 0x9B270/0xA0B70 (hideInfoDialog) and 0x9B3C0/0xA0CA0; 0x9ADF0/0xA1910 (showInfoDialog) are close. Only B uses place_object and sell_action_prompt, and "PlaceTitleBar" (0x2E7100, no references) sits just before B's vtable. `names set` rejects duplicate names, so batch 4 skipped all 13.
Batch 5 settled which is which: the pause constructor 0xA80B0 builds +0x6C with 0xA1B00 and +0x1288 with 0x9F540; SetPauseVariable sends message 0x12 for "draw_buy" and 0x13 for "draw_build"; HandlePauseMessage turns 0x12 into mode 4 on this+0x6C and 0x13 into mode 5 on this+0x1288; DrawPauseMenuText takes mode 4's category from the table starting "seating_beds" (0x3097C0) and mode 5's from the table starting "walls" (0x3097E8); and only the buy class's slot 2 (0x9F720) calls UpdateBuyActionButton. Class B is the buy menu and class A the build menu. No string states either class name, so their names stay flat with Buy and Build qualifiers.
The M2b follow-up pass (2026-10-12) named the pairs: UpdateBuildMenu/UpdateBuyMenu (slot 1), HandleBuildMenuMessage/HandleBuyMenuMessage (slot 6), UpdateBuild/BuyInfoLozenges, ShowBuild/BuyInfoDialog, HideBuild/BuyInfoDialog, and DrawBuyMenu (slot 2). 0x9B3C0 and 0xA0CA0 are not vtable slots: each is called by its class's destructor (0x9BAB0, 0xA0DD0) and by 0xA8220, hides the info dialog and frees the members, so they are ShutdownBuildMenu and ShutdownBuyMenu, after ShutdownHUD. The constructors 0x9F540 and 0xA1B00 reference no string and stay unnamed. The build menu's slot 2 has no function (F-0065).
- Revisit when: a string or the GameCube donor states the class names.
## F-0042 The HUD and load-bar screen classes have no stated names
- Status: open
- Addresses: 0x002E6888, 0x002E62A8, 0x00096000, 0x00096220, 0x00095E00, 0x0008FD20, 0x0008EC70, 0x002E6A88, 0x00097390, 0x000975F0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0x96000 installs vtable 0x2E6888 and calls 0x95E00, which fills a command-handler table at +0x58..+0x114 (ChangeToPreviousSim +0x68, ChangeToNextSim +0x6C, PauseGame +0xD0, OpenIngameChat +0xD8). The destructor 0x96220 calls ShutdownHUD. Slots 1, 2, 7 and 8 are UpdateHUD, DrawHUD, SetHUDVariable and GetHUDVariable, the slots the CAS and HouseSelect screens use (F-0039). No string states the class name; 0x8FD20 and 0x8EC70 pass "hud" (0x2E62A8) to the Flash "loadFunctions" call 0xFD4E0, as LoadTrans does with "trans", and the variables use the prefix `hud_`. Batch 4's flat HUD names rest on these. The load-bar class (vtable 0x2E6A88) is the same case: its methods call showLoadBar, hideLoadBar and resetLoadBar, and its only variable is loadbar_ready.
- Next: slot 8 of the load-bar vtable (0x975F0) is named GetLoadBarVariable (F-0040). Slot 1 of the load-bar vtable (0x97390) and slot 2 of the CAS (0x1D870) and HouseSelect (0x7CC20) vtables reference no string, so they are named when they are matched (ADR-0009). Revisit the names if a string or the GameCube donor states a class name.

## F-0043 The pause screen class has no stated name, and its Draw slot 0xADA10 is not a function
- Status: open
- Addresses: 0x002E7578, 0x000A80B0, 0x000ADA10, 0x000ACB50, 0x000A8C40, 0x000A82C0, 0x000ACB80, 0x000C0420
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Vtable 0x2E7578 has slot 0 0xACB50, slot 1 UpdatePause, slot 2 0xADA10, slot 6 HandlePauseMessage, slots 7 and 8 Set/GetPauseVariable, slot 17 InitPauseMenu and slot 18 0xA8C40, which undoes slot 17. The names rest on the Flash calls showPause, hidePause and showMainPause and the pause_ prefix, as in F-0042. 0xADA10 is referenced only from the vtable (0x2E7580) and holds the calls to DrawPauseMenuText (0xADA9F, 0xADAD6, 0xADAF0) and DrawGameTime (0xADB2B), but Ghidra has no function there and the gap report does not list it. Batch 3's SetPauseMenuItemText (0x78AE0) belongs to the HouseSelect class's own pause menu, not to this class, although both drive the same Flash pause movie.
M2b Task 7 (2026-10-12) created 0xADA10 as a 345-byte function. The strings export lists no string for it, so under ADR-0009 it keeps its auto name; DrawPause is the name a vtable-slot reading suggests.
- Next: name 0xADA10 when it is matched (ADR-0009). The class name is still unknown.

## F-0044 Slot 6 of the screen vtables dispatches a message id
- Status: open
- Addresses: 0x000A8CC0, 0x00090310, 0x00020EF0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Pause slot 6 (0xA8CC0, HandlePauseMessage) switches on the id in its second argument and forwards unhandled ids to the owner's slot 6; its own code sends ids through `call [vtbl+0x18]`. HUD slot 6 (0x90310) calls handler[id] from the table at +0x48 (F-0042). CAS slot 6 (0x20EF0, 7,125 bytes) references showDialog like the pause handler.
The M2b follow-up pass (2026-10-12) named 0x20EF0 HandleCASMessage: it switches on the id in its third argument and calls showDialog, hideMenu, HideCAS and ShowCAS. The build and buy menu slot-6 handlers also dispatch on an id but return on unknown ids instead of forwarding them.
- Next: name 0x90310 when it is matched (ADR-0009). It references no string, so `names set` cannot record it.

## F-0045 One info dialog class (vtable 0x2E7318) serves the buy menu, the build menu and the pause goal list
- Status: open
- Addresses: 0x002E7318, 0x000A5830, 0x000A7E60, 0x000A6DC0, 0x000A6F60, 0x000A4540, 0x000A3650, 0x000A6200, 0x000A5950
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0xA5830 sets mode +0x3BC to 0 and is called by the build menu (0x9ABB0, 0x9ADF0) and the buy menu (0xA1910). The constructor 0xA7E60 takes the mode as an argument; HandlePauseMessage passes 1 for message 0x10 ("draw_goals"). Slot 2 (0xA6DC0) calls DrawBuyItemInfo for mode 0 and DrawInfoMenu for mode 1, so "Buy" in DrawBuyItemInfo means an item for sale, not the buy menu alone. UpdateBuyActionButton is a non-virtual member called only by the buy menu. No string states the class name, so batch 5 left its constructors, Update (0xA6F60), Draw (0xA6DC0) and layout initializer (0xA4540) unnamed.
- Next: choose a label for the class (InfoDialog follows its show/hideInfoDialog and show/hideInfoArrow Flash calls), or revisit if a string or the GameCube donor states it.

## F-0046 The save-file wrappers at 0xBDFD0..0xBF8A0 call an unidentified save interface at 0x39E858
- Status: open
- Addresses: 0x0039E858, 0x00098980, 0x000988C0, 0x000BDFD0, 0x000BE020, 0x000BE160, 0x000BE2E0, 0x000BE320, 0x000BE400, 0x000BF8A0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Seventeen small functions call slots 0x14, 0x1C, 0x20, 0x28, 0x80, 0x84 and 0x88 of the object at 0x39E858 on the files "Config" (0x2E83D8) and "SaveGame" (0x2E83E4). Slot 0x88 opens, 0x1C reads (0x98980 then checks a checksum and the magic 0x20A0B0D) and 0x20 writes (0x988C0); the rest and the helpers 0x18CDD0, 0x1C64A0, 0x18DAE0, 0x1C6D00, 0x18D440 and 0x18BE60 are unnamed. 0xBE020 passes "BASLUS-20842", the PS2 NTSC-U product code, as the save title. Batch 5 named LoadConfig (0xBDFD0, no references in Ghidra) and SaveConfig (0xBE320); 0xBE2E0 is a second "Config" loader (0x98980, 0x98590, slot 0x14) and needs a different name.
- Next: identify the interface's vtable and its slots, then name the remaining wrappers.

## F-0047 The Keyboard, ErrorPopup, UnlockDialog and MU screen classes have no stated names
- Status: open
- Addresses: 0x002E8890, 0x002E89C0, 0x002E8EF0, 0x002EA840, 0x002E3EE0, 0x0004CF60, 0x0004F480, 0x000C9BB0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: As in F-0039 and F-0042, batch 6's flat names rest on Flash calls and variable prefixes. Keyboard (vtable 0x2E8890): showKeyboard and hideKeyboard, Keyboard* variables, the "Keyboard" table; slots 2, 7 and 8 are DrawKeyboard, SetKeyboardVariable and GetKeyboardVariable, and slot 1 is the base 0x124940. ErrorPopup (0x2E89C0): LoadErrorClassA, removePopup and Error* variables; slots 1, 2, 7 and 8 are 0xC9A80, DrawErrorPopup, SetErrorPopupVariable and GetErrorPopupVariable. UnlockDialog (0x2E8EF0): showUnlockDialog and hideUnlockDialog and unlock_dialog_ready; slots 18 to 22 are shared with the base dialog vtable 0x2E3EE0, slot 23 (SetUnlockDialogMessage) overrides the base hook 0x4CF60, and slots 25 and 26 (0xCE660, InitUnlockDialogLayout) are new; its destructor ends in DestroyDialog. MU (0x2EA840): mu_* calls and variables and MUStrings; slots 2, 7 and 8 are DrawMU, SetMUVariable and 0xD8030. The constructors are in-place (base constructor 0x1249C0, vtable, return this), so the reviewer renamed CreateKeyboard and CreateErrorPopup to ConstructKeyboard and ConstructErrorPopup, and WORKFLOW now states the Construct/Destroy rule. Slot 0 holds a separate deleting destructor (0xC9BB0 calls DestroyKeyboard, then frees the object if bit 0 is set).
- Next: name the remaining slots (ErrorPopup slot 1 0xC9A80; UnlockDialog slots 1 and 2, 0xD17A0 and 0xD0820; MU slots 1 and 8, 0xDA940 and 0xD8030), choose a name pattern for the slot-0 deleting destructors, and revisit if a string or the GameCube donor states a class name.

## F-0048 A second dialog class (vtable 0x2EA2A8) uses the game dialog's Flash and variable names, which blocks unique names
- Status: open
- Addresses: 0x002EA2A8, 0x000E3280, 0x000E3310, 0x000D6090, 0x000D6190, 0x000D6200, 0x000D6240, 0x000D6290, 0x000D6330, 0x000D6860, 0x000D68D0, 0x000D7030
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0xE3280 installs vtable 0x2EA2A8 and has four callers (0xE3360, 0xE3650, 0xF9780, 0xF9AE0) in front-end state code near CreateASimBaseState::Update and TheSimsEnterMainMenuState::Update. Slots 1, 2, 7 and 8 are 0xD6090, 0xD6190, 0xD6290 and 0xD6330. It calls Flash through 0xDF7F0 rather than 0xFD140, falls back to base handlers 0xE03F0 and 0xDF330, and 0xD6330 appends " >> no support <<" for unknown keys. It uses the game dialog's strings (showDialog, hideDialog, dialog_title_bar, dialog_status, dialog_box_width), so its natural names collide with ShowDialog, SetDialogVariable and GetDialogVariable. 0xD6200 and 0xD6240 have no references and are 0xD68D0 and 0xD6860 without the reset and free steps. Batch 6 skipped all eight.
- Next: choose a qualifier (for example FrontEnd, after its callers) or find the class name in the GameCube donor, then name the eight.

## F-0049 0xD49E0 is an unreferenced twin of SubstituteXboxButtonNames
- Status: open
- Addresses: 0x000D49E0, 0x000D4180, 0x000D39D0, 0x000D3A80
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0xD49E0 has no references. It reads the same LiveModeMenuUIStrings button keys and the same global tokens (0x32188C and on) as SubstituteXboxButtonNames (0xD4180), but replaces through 0xD3A80 instead of 0xD39D0 and takes its text through a 0x100-character buffer (0x1A4F10, 0x1A49A0), which looks like a different string type. Batch 6 skipped it because names must be unique.
- Next: name it as a variant that says how it differs, for example by the string type.

## F-0050 The MainMenu, UnlockTradeDialog and Option screen classes have no stated names
- Status: open
- Addresses: 0x002EB148, 0x000F95E0, 0x000F9930, 0x002EB230, 0x000FAEE0, 0x002EA8A8, 0x000F3670, 0x000F2B00
- Checked: ghidra-mcp (2026-10-11)
- Evidence: As in F-0039, F-0042 and F-0047, batch 7's flat names rest on Flash calls and variable prefixes. MainMenu (vtable 0x2EB148, movie name "menu"): loadMainMenu, unloadMainMenu and menu_ variables; slots 1, 2, 7 and 8 are 0xDBA50, 0xDB270, SetMainMenuVariable and GetMainMenuVariable; 0xF9930 allocates it, calls the constructor 0xF95E0, then InitMainMenu. UnlockTradeDialog (vtable 0x2EB230, constructor 0xFAEE0): showUnlockTradeDialog, hideUnlockTradeDialog, unlockTrade_setConfiguration and unlkTrad_ready; slots 1, 2, 7 and 8 are 0xDD570, 0xDCCB0 (outside any function, F-0026), SetUnlockTradeDialogVariable and GetUnlockTradeDialogVariable. Option (vtable 0x2EA8A8): showOption, hideOption, optionReset, the button context "option" and option_button_* variables; slots 0, 1, 2, 7, 8 and 19 are the deleting destructor 0xF2B00, UpdateOption, 0xF3DD0, SetOptionVariable, GetOptionVariable and ShowOption. "OptionsMenu", from the text key options_menu_title, was the other candidate label.
- Next: name UpdateMainMenu (0xDBA50), DrawMainMenu (0xDB270), the UnlockTradeDialog slots 1 and 2, and DrawOption (0xF3DD0). Revisit if a string or the GameCube donor states a class name.

## F-0051 UnlockTradeDialog receives trade messages through a handler interface at +0x5C
- Status: open
- Addresses: 0x002EB228, 0x000DD270, 0x000DCE00, 0x000DC8C0, 0x001B8C90, 0x00310CB8
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The constructor 0xFAEE0 installs the interface vtable 0x2EB228 ([0xDD270, 0xDCE00]) at +0x5C, and InitUnlockTradeDialog stores this+0x5C at [0x310CB8]+0xEC. 0x1B8C90 calls slot 0 of that pointer with (id, player, arg) and, when [0x35D3C0]+0x14C is 1, also sends the triple as a 13-byte packet tagged 0x7F. 0xDCE00 (slot 1) switches on input ids 0..4 and posts ids 1, 2, 6 and 7 through 0x1B8C90; 0xDC8C0 posts id 5. 0xDD270 acts on ids 1, 2, 5, 6 and 7, so it receives messages rather than raw input; the reviewer renamed it HandleUnlockTradeMessage. That the other player's packets reach the same slot is a guess: the receive path was not traced.
- Next: trace the 0x7F packet receive path, then name 0xDCE00 (for example HandleUnlockTradeDialogInput) and 0x1B8C90.

## F-0052 The front-end "ContextButton" functions belong to an unnamed button-widget base class
- Status: open
- Addresses: 0x000DF3F0, 0x000DF4B0, 0x000DF570, 0x000DF610, 0x000E0BD0, 0x000DF210, 0x00309A90, 0x000DF010, 0x000E0910, 0x000DF330, 0x000E03F0
- Checked: ghidra-mcp (2026-10-11)
- Evidence: The class holds a Flash button-context name at +0x38 (length at +0x3C), up to 7 button widgets at +0x40 indexed by the name table 0x309A90 (accept, decline, alt1 and four more), and a created-bit mask in bits 8..14 of +0x08. Every method wraps its Flash calls in setButtonContext(+0x38) and resetButtonContext. CreateContextButton allocates a 0x70-byte widget (0xD9A30) when the slot is empty, then calls createButton(name, "center"). ParseButtonVariableName parses "[context_]button_<name>_x|y|width" for the base handlers 0xDF330 and 0xE03F0, which F-0048's class also uses. Its Draw (0xDF010, in six vtables) and destructor (0xE0910, called by six derived destructors) stay unnamed; no string states the class name.
- Next: choose a label for the class, then name 0xDF010 Draw<X> and 0xE0910 Destroy<X>.

## F-0053 0xE8FF0 creates a shared front-end overlay at global 0x321C40, not a copyright object
- Status: open
- Addresses: 0x000E8FF0, 0x000E8D30, 0x00321C40, 0x002EA260, 0x000E8E10, 0x000F6F70
- Checked: ghidra-mcp (2026-10-11)
- Evidence: 0xF6F70 (slot 1 of state vtable 0x2EAD38) calls 0xE8FF0 on 0x321C40. When +0xFC is empty, 0xE8FF0 allocates and constructs a screen with the generic vtable 0x2EA260 and a widget (0xE8E10), caches two elements at +0x104 and +0x108, hides the second and sets its text to start_screen_copyright. 0xE8D30 shows the +0x100 widget and stores a duration and its reciprocal at +0x128..+0x130; ShowOverwriteDialog, CreateASimBaseState::Update and 0x8EC70 call it, so the overlay is shared. Batch 7 named 0xE8FF0 CreateStartScreenCopyright and the reviewer cleared it: the copyright is only the text of a hidden element. That the overlay is a fade or transition is a guess from the duration fields.
- Next: identify the class at 0x321C40 (0xE7150, 0xE7CB0, 0xE7D80, 0xE7E30), then name 0xE8FF0 and 0xE8D30.

## F-0054 Front-end state vtables have six slots, with Update in slot 4
- Status: open
- Addresses: 0x002EACA8, 0x000E2700, 0x002EAD20, 0x000E3650, 0x000E2DE0, 0x002EAF90, 0x000E1370, 0x000E3360
- Checked: ghidra-mcp (2026-10-11)
- Evidence: Each state vtable at 0x2EAC80..0x2EB000 is [destructor, s1, s2, s3, s4, s5]. CreateASimBaseState's has the destructor 0xF8110 and CreateASimBaseState::Update in slot 4. CreateLoadGameDialog (0xE3360) is slot 1 of four vtables (0x2EACDC, 0x2EAE44, 0x2EAEEC, 0x2EAFC4); in 0x2EAD20, slot 1 is CreateSavePromptDialog and slot 3 is ShowOverwriteDialog; in 0x2EAF90, slot 1 is 0xE1370. That slot 1 builds the state's UI and slot 3 shows it again is a guess from these examples. Batch 8 (2026-10-12): the credits state vtable 0x2EB128 is [0xF95A0, CreateCreditsDialog, 0xF9120, 0xF9EA0, 0xF7CA0, 0xF8860], and CreateNotPastMomsHouseDialog is slot 1 of 0x2EAE14; both fit slot 1 building the state's UI.
- Next: confirm the slot roles across more states before naming the slot-1 and slot-3 functions of unnamed states.

## F-0055 Flash and Apt in function names are labels, not stated class names
- Status: open
- Addresses: 0x000FB330, 0x000FB530, 0x000FB7B0, 0x000FBBB0, 0x000FBDE0, 0x000FC820, 0x000FD4E0, 0x000FD510, 0x000FE8F0, 0x000FEAD0, 0x0010C760, 0x0010CB30, 0x00110350, 0x00111A80, 0x00119FF0, 0x0011C620
- Checked: ghidra-mcp (2026-10-12)
- Evidence: Batch 8 labels the game's wrappers in 0xFB000..0xFF000 "Flash" and the ActionScript runtime in 0x10A000..0x11D000 "Apt". Strings state "Flash\", "Flash animation" and "_level0" on the wrapper side (0xFB120, 0xFBBB0, 0xFC820), and ".apt", ".const", "Apt PCGL geometry file" and "Apt Case Problem" on the runtime side (0xFBDE0, 0xFB7B0, 0x10CB30). The other Apt names (0x111A80, 0x119FF0, 0x11A680, 0x11C620 and others) rest on the address range and on being ActionScript interpreter code (onPress, __proto__, charAt), and 0xFD4E0, 0xFE8F0 and 0xFEAD0 on their loadFunctions, addButton and removeButton calls through the Flash bridge (F-0042). SetFlashVariable and GetFlashVariable cite no Flash string; they follow the SetDialogVariable pattern. The batch 8 reviewer accepted the split.
- Evidence (batch 9): The Date, Math and Array labels on GetAptDateMethod 0x0011D940, GetAptMathFunction 0x0011F2F0 and GetAptArrayProperty 0x00120990 rest on full JavaScript member lists and on separate dispatcher type checks (0x001147A0, 0x0010A590 for type 0x17, 0x00114710); RegisterAptGlobalClasses 0x00110350 registers a class named "Array". The Key label on GetAptKeyMethod 0x0011FAC0 rests on behaviour: its cached getCode object 0x0011F1A0 returns the last key code from DAT_0035BEA4, uppercased or mapped through the table at 0x002EC030, as ActionScript Key.getCode() does. The namer had called it Controller from the "getController" string, which stays unexplained. The dispatcher 0x001160E0 selects it for type 0x18 (check 0x0010A560).
- Next: replace the labels with class names if the GameCube donor or a string names the Apt player classes.

## F-0056 Two front-end state Updates log the mode they switch to
- Status: open
- Addresses: 0x000F4190, 0x002EAB6C, 0x000F4240, 0x002EAB90, 0x000F5480
- Checked: ghidra-mcp (2026-10-12)
- Evidence: 0x000F4190 (in vtable 0x2EAB6C) logs "Start Mode\n" and 0x000F4240 (in vtable 0x2EAB90) logs "Loading...\n" before switching state through 0x000F5480. The logged text names the target mode, not the state that owns the Update, so batch 8 left both unnamed.
The M2b follow-up pass (2026-10-12) mapped the table. 0xF4A10 builds 0x14-byte states {vtable, id, 0, -1, 1}: id 0 0x2EAB6C, id 1 0x2EAB90, id 2 0x2EABCC, id 3 0x2EABE4, id 4 0x2EABB4, id 5 0x2EABFC, with Update in slot 4. 0xF4190 is state 0's Update: it waits until the float in DAT_00321E00 reaches 0.25, then switches to state 1 and logs "Start Mode\n". 0xF4240 is state 1's Update: it switches to state 2, or logs "Loading...\n" and switches to state 4 (state 7, which is not in this table, when DAT_00310D50 is set). No string names a state, and the logs fit both "state 0 is Start" and "each logs its target", so both stay unnamed. The other Updates 0xF4350 (state 4), 0xF4480 (state 2) and 0xF45E0 (state 3) reference no strings.
- Next: name the states when a state-class string or the GameCube donor states them.

## F-0057 The EResourceManager::AddRef string is shared by a lookup and a loader
- Status: confirmed
- Addresses: 0x002EC220, 0x00122500, 0x00122C50, 0x001225D0
- Checked: ghidra-mcp (2026-10-12)
- Evidence: Both functions log "EResourceManager::AddRef() tried to load resource of type %s with ID of 0" when the id is 0, and both read the type name from this+0x40. 0x00122500 only locks, looks up an existing entry by id and returns it or 0; GetResourceByName 0x001225D0 calls it. LoadResourceById 0x00122C50 loads through slot 0x28 of the factory at DAT_0035E0F0 when the entry is absent and logs "Invalid resource" and "not found". Neither shows a reference-count increment, so the string does not make either one AddRef. Batch 8 left 0x00122500 unnamed. The M2b follow-up pass (2026-10-12) named it GetResourceById: it has 43 call sites in 22 functions, all of which pass an id, and its name pairs with GetResourceByName. The reviewer did not inspect the callers one by one.
- Revisit when: a caller treats the result as a reference-counted handle.

## F-0058 0x00121E50 is a tagged allocator that retries after freeing memory
- Status: confirmed
- Addresses: 0x00121E50, 0x00122B90, 0x00135520, 0x001355C0, 0x00135620, 0x00136E90, 0x00137550, 0x00137710, 0x00135730
- Checked: ghidra-mcp (2026-10-12)
- Evidence: It takes (size, align, file, line, tag), calls an allocation slot of its object, and on failure frees memory through 0x00121D30 and retries, breaking into the debugger after a final 0x00123060 failure. 0x00122B90 calls it with alignment 4 and serves as the tagged operator new. The SetSize functions 0x00136E90, 0x00137550 and 0x00137710 and GetERModelScaleMatrix 0x00135730 store its result and null-check it. AllocModelStripArray, AllocSubModelShaderArray and AllocSubModelArray pass a size and alignment with the SetSize file, line and tag fixed, which supports their Alloc names.
- Revisit when: a string or the GameCube donor names the allocator, so 0x00121E50 can be named.

## F-0059 InitEXBoxRC calls a shared base init before allocating its matrix buffer
- Status: open
- Addresses: 0x0015B9F0, 0x0014D3C0, 0x002EE3F8, 0x002EDB4C
- Checked: ghidra-mcp (2026-10-12)
- Evidence: 0x0015B9F0 is slot 5 of the vtable at 0x002EE3F8. It first calls 0x0014D3C0 on the same object, which stores the device argument at +0x10, sets counters and allocates 0x1000 bytes through 0x00179EA0, and is also referenced from the vtable at 0x002EDB4C. It then allocates the 0x200000-byte "EXBoxRC Matrix Buffer" once, guarded by DAT_0035E300. The namer called it AllocEXBoxRCMatrixBuffer; the reviewer renamed it InitEXBoxRC because the buffer is only part of the work. The Init verb comes from the code, not from a string.
- Next: name 0x0014D3C0 once the class that owns the vtable at 0x002EDB4C is known.

## F-0060 ShowDiscErrorScreen ignores the failure text its callers pass
- Status: confirmed
- Addresses: 0x0016B810, 0x0016B450, 0x00173220, 0x0017F600, 0x0017FC10, 0x0015EC00, 0x00188A10, 0x00188B00, 0x00188BC0, 0x00189020
- Checked: ghidra-mcp (2026-10-12)
- Evidence: 0x0016B810 has ten callers. ConstructMovie, DrawMovieFrame, ReadAudioStreamData, BeginAudioStreamRead and InitAudioSystem push a "failed ..." string before the call, and four unnamed functions at 0x00188A10..0x00189020 call it too. The decompiled body takes no parameter: it sets DAT_0039FD00, resets the device, draws a "problem with the disc" message chosen by XGetLanguage with XFONT, and loops forever. The callers' "failed ..." strings are therefore never shown or logged, so they describe the caller's failure and not this function.
- Revisit when: the four unnamed callers are named, or a debug build shows the argument in use.

## F-0061 ERAnim has an unnamed create callback and three arrays that share one SetSize tag
- Status: confirmed
- Addresses: 0x0017DB40, 0x00146350, 0x001462B0, 0x0017DBD0, 0x0017D760, 0x0017DC80, 0x0017D060, 0x0017D080, 0x0017D140, 0x0017D460, 0x0017D670, 0x0017DA30, 0x002EFEE4
- Checked: ghidra-mcp (2026-10-12)
- Evidence: 0x0017DB40 allocates 0x9C bytes with the "ERAnim operator new" tag, calls the constructor 0x0017D760 and returns the object; it is the create callback passed by RegisterERAnimClass 0x0017DBD0 and is also referenced from 0x00242A00. CreateERAnim 0x00146350 does the same and then calls 0x0017DC80 with its argument, which matches the CreateERRleTexture and CreateERRleTextureFromStream pair of F-0033 if 0x0017DC80 reads a stream. The tag "ERAnim TArray SetSize" (0x002EFEE4) is used by five functions: 0x0017D060 and 0x0017D080 are bare allocator calls, and the three SetSize functions differ only in the code (4-byte elements through 0x00122B90 at e_ranim.h line 0x2D; 0x50-byte and 0x20-byte elements through 0x00121E50 with 16-byte alignment at line 0x2E). The batch 11 reviewer named those three SetERAnim<N>ByteArraySize after the Set<X>ArraySize names of batch 9, with the element size taken from the code.
The M2b follow-up pass (2026-10-12) settled it: 0x0017DC80 reads from its stream argument through the stream's slot 0x10 and helpers 0x138310, 0x1528E0 and 0x17D990. 0x00146350 is renamed CreateERAnimFromStream and 0x0017DB40 is named CreateERAnim.
- Revisit when: ERAnim's layout is recovered; then replace the element sizes in the three names.

## F-0062 LookupRumbleDataElement returns the element it looks up
- Status: confirmed
- Addresses: 0x0019B270, 0x00142D90, 0x00142EA0, 0x002F1200
- Checked: ghidra-mcp (2026-10-12)
- Evidence: The disassembly pushes the table name 0x002F1200, calls 0x00142D90, then calls 0x00142EA0 with the key and returns with RET 4, so the lookup result in EAX is the return value. It is a __thiscall with one stack argument that reads [this+0x664]. Ghidra shows a void return only because the prototype is unset. The batch 12 namer had said the function discards its result, and the batch 12 reviewer corrected that.
- Revisit when: prototypes are set; give it a __thiscall signature with one stack argument and a pointer return.

## F-0063 0x00142D90 is a name-keyed table lookup, so its callers look up rather than load
- Status: confirmed
- Addresses: 0x00142D90, 0x00142CC0, 0x001F2D60, 0x001F2D90, 0x001F2E10, 0x001F2E70, 0x001F2EA0, 0x001F33F0, 0x0019B270
- Checked: ghidra-mcp (2026-10-12)
- Evidence: 0x00142D90 returns 0 for a null name. Otherwise it binary-searches an array of 0x14-byte entries through 0x00142CC0 and returns a pointer to the entry, or 0. It has 112 callers. The five snd functions at 0x001F2D60 to 0x001F2EA0 only call it with a "snd::..." string and store the result in a member, so the batch 13 reviewer renamed them from LoadSnd* to LookupSnd*. InitSndTypes 0x001F33F0 makes the same lookups and also allocates objects, so it keeps Init. LookupRumbleDataElement 0x0019B270 (F-0062) calls it too.
- Revisit when: 0x00142D90 gets a name; use the same verb for its other callers.

## F-0064 Five class dynamic initializers pass a nonzero class id
- Status: open
- Addresses: 0x00241DC0, 0x00241E10, 0x00241EB0, 0x00242A00, 0x00242B10, 0x0012E8D0, 0x00137500, 0x001550C0
- Checked: ghidra-mcp (2026-10-12)
- Evidence: Of the 30 class-record initializers named in M2b batch 14, DynamicInit_ERLevelClass 0x00241DC0 and DynamicInit_ERShaderClass 0x00241E10 pass id 2 to 0x001550C0, DynamicInit_ERModelClass 0x00241EB0 passes 1, and the rest pass 0. Batch 15 named 17 more: DynamicInit_ERAnimClass 0x00242A00 passes 1 and DynamicInit_EIEffectorClass 0x00242B10 passes 5. The out-of-line Register functions 0x0012E8D0 and 0x00137500 take the id as their first argument.
- Next: find what the 16-bit id in the class record controls.

## F-0065 The build menu's Draw slot 0x9C6B0 is not a function
- Status: open
- Addresses: 0x0009C6B0, 0x002E6E40, 0x002E6E38, 0x0009F720
- Checked: ghidra-mcp (2026-10-12)
- Evidence: Slot 2 of the build menu vtable 0x2E6E38 (the pointer at 0x2E6E40) references 0x9C6B0, but Ghidra has no function at or containing it. The bytes start with an SEH prologue and `sub esp,0x324`, then test bit 1 of [this+0x1C], the same check DrawBuyMenu 0x9F720 makes in the buy menu's slot 2. Whether the gap report lists it was not checked.
M2b Task 7 (2026-10-12) created 0x9C6B0 as a 9114-byte function ending at 0x9EA4A, between 0x9BB20 (ends 0x9C68A) and UpdateBuildMenu 0x9EAB0. The strings export lists no string for it, so under ADR-0009 it keeps its auto name; DrawBuildMenu is the name a vtable-slot reading suggests.
- Next: name 0x9C6B0 when it is matched (ADR-0009).

## F-0066 symbols.txt gave 0x206070 a size of 25 bytes; the function is 44
- Status: confirmed
- Addresses: 0x00206070, 0x00206040, 0x002060A0
- Checked: ghidra-mcp (2026-10-12)
- Evidence: The sync export after the M2b Task 7 function creations changed the size of 0x206070 from 25 to 44. In Ghidra the body runs from 0x206070 to 0x20609B and ends with `RET 0x8` at 0x206099, so 44 is the correct size. The 25-byte entry ended at 0x206089, inside the loop. It came from M2a. Its neighbours 0x206040 (43) and 0x2060A0 (42) are functions of the same shape. Why Ghidra's body changed between M2a and this export is not known; that the analysis run by create_function extended it is a guess.
- Revisit when: another size changes in a sync export without a function being created or deleted at that address.

## F-0067 The project agent types did not load in the session that started M2b Task 6
- Status: confirmed
- Addresses: none
- Checked: session tool list (2026-10-11, 2026-10-12)
- Evidence: When M2b Task 6 began, the Agent tool listed only the built-in agent types, not `namer`, `reviewer` or `matcher` from `.claude/agents/`. Batches therefore ran on general-purpose agents told to follow `namer.md` or `reviewer.md`. Those agents did not get the frontmatter tool limits, so the reviewer prompt forbade writes and the lead checked `git diff` and `sync check` after each review. On 2026-10-12, after the context was compacted, the same session listed all three project types. Why they were missing at first is not known.
- Revisit when: a session lacks the project agent types again; check the tool list before dispatching a batch.

## F-0068 Plans that change the Ghidra project run in the main checkout, not a worktree
- Status: confirmed
- Addresses: none
- Checked: repository layout (2026-10-11)
- Evidence: The Ghidra project (`ghidra/`), `orig/` and `build/` are gitignored, so a git worktree has none of them. M2a and M2b therefore ran on a branch in the main checkout. Nothing shared was changed before the merge.
- Revisit when: the Ghidra project or the build inputs move into git or become shared between checkouts.

## F-0069 A match shows that addresses agree, not that declared types or classes are right
- Status: confirmed
- Addresses: 0x00011400, 0x00027EF0, 0x00032E50, 0x00058000
- Checked: test bodecomp.match (2026-10-12), M3 batch 1 review against ghidra-mcp
- Evidence: The relocation rule compares the address each relocation site resolves to. The class a callee is declared in and the type of a global are not part of the comparison. In batch 1, `FUN_00124700` is a member of the stand-in structs `S_00032E50` and `S_00058000`, and `DAT_0035d220` is declared `int` although only its address is used. A swapped callee, global or vtable slot is still caught, because the address or the slot offset differs.
- Revisit when: the types of these functions are recovered; until then their declarations are provisional.

## F-0070 0x00050620 matches only with a temporary that loads the float first
- Status: confirmed
- Addresses: 0x00050620
- Checked: test bodecomp.match (2026-10-12)
- Evidence: The target loads `DAT_002e21ac`, stores the byte at +0xD8, then stores the float at +0xDC. `float v = DAT_002e21ac; flag = true; value = v;` matches. `flag = true; value = DAT_002e21ac;` scores 37.5 and `value = DAT_002e21ac; flag = true;` scores 50.0. The reviewer accepted the temporary as ordinary source.
- Revisit when: a recovered source for this class shows another shape.

## F-0071 0x00058000 uses 21 placeholder virtual functions to reach vtable slot 20
- Status: open
- Addresses: 0x00058000
- Checked: ghidra-mcp (2026-10-12)
- Evidence: The call is through `[EDX+0x50]`, slot 20. The stand-in struct declares `v0` to `v20` only to place the call there.
- Next: replace the placeholders with the real class and slot names once the owning class is identified.

## F-0072 A compiler-emitted vtable, a float literal, a string literal and a callee resolved by its real name all match without special handling
- Status: confirmed
- Addresses: 0x0001BC70, 0x00048D70, 0x00163790, 0x0006BA00
- Checked: bodecomp.match and the reviewer, M3 batch 2 (2026-10-12)
- Evidence: Declaring three virtual functions named `FUN_0001bc80`, `FUN_00199310` and `FUN_00199320` makes VC71 emit a vtable whose bytes and pointers match the XBE at 0x2E2980, and there is no RTTI locator. `1.0f / (float)count` emits a local float equal to the XBE bytes at 0x2E21B8. Returning `"N/A"` emits a literal equal to the bytes at 0x2EE9EC. `void LoadSignStrings();` decorates to `?LoadSignStrings@@YAXXZ`, whose scope path names the string-tier entry at 0x0006B4E0.
- Revisit when: the resolver rules in bodecomp.match change.

## F-0073 VC71 at /O2 inlines 0x000FAE60 into 0x000FAED0 when both are in one file, but the target keeps the call
- Status: confirmed
- Addresses: 0x000FAED0, 0x000FAE60
- Checked: bodecomp.match and the reviewer, M3 batch 2 (2026-10-12)
- Evidence: With both member functions in one file, in either definition order, the built 0x000FAED0 contains the callee's body and no call; the target has `call 0x000FAE60`. 0x000FAED0 is parked as `unclassified` at 7.7. That the callee was defined in another file of the original build is a guess; different inlining flags (compare F-0018) would also explain it. Because of this, the same-file call path of bodecomp.match is still untested on real code.
- Resolved (2026-10-12): with 0x000FAED0 moved to its own file, src/game/auto/000FAED0.cpp, it matches at 100 and calls 0x000FAE60 through a relocation to another file. That needed the placeholder names in `FUN_XXXXXXXX` form: the resolver maps only that form to an address, and `fn_000fae60` failed with "names 0 entries in symbols.txt". That the original build also had the two in separate files rests on this match; other inlining flags were not tried. No `inlining` blocker class is needed. The same-file call path of bodecomp.match is still untested on real code.

## F-0074 The trivial generator's global types are byte-correct placeholders, not evidence of width
- Status: open
- Addresses: 0x0030D44C, 0x001F77E0, 0x001F7810
- Checked: ghidra-mcp, reviewer of the gen_trivial batch (2026-10-12)
- Evidence: bodecomp.trivial declares every global it reads with `a1` as `extern int`, or as `extern short` for the `66 a1` pattern, and every global it writes as `extern int`. These match the bytes because the instruction fixes the access width. Ghidra types 0x0030D44C as undefined2; 0x001F7810 reads it with a 16-bit `movzx` and writes it with a 32-bit `mov` at 0x001F7827, and the bytes at 0x0030D44C are 01 00 00 00. Whether it is a short followed by two other bytes or an int is unsettled. src/game/trivial/001F.cpp declares it `int`.
- Next: when a namer reaches the RNG at 0x001F7810, decide the width from the other users of 0x0030D44E and retype it. Do not read a type from the generated declarations.

## F-0075 Ghidra ends 0x00013730 at a mid-function int3, so its size is 11 bytes instead of 17
- Status: open
- Addresses: 0x00013730, 0x0001373B
- Checked: ghidra-mcp, matcher and reviewer of M4 batch 1 (2026-10-12)
- Evidence: The bytes at 0x00013730 are `80 7c 24 04 00 74 03 33 c0 c3 cc b8 01 00 00 00 c3`, 17 bytes. Ghidra gives FUN_00013730 a size of 11, ending at the `cc`, and the `mov eax,1; ret` at 0x0001373B belongs to no function and has no references. The unit in build/target/units.txt runs from 0x00013730 to 0x00013750, and the source `if (a) return 0; __debugbreak(); return 1;` in src/game/auto/0001.cpp matches all 17 bytes. Whether other functions are cut at an int3 that is not padding is unchecked.
- Next: have a namer set the size of 0x00013730 to 17, and check whether `bodecomp.gaps` reports 0x0001373B and other code after an int3 inside a unit.

## F-0076 0x000E17A0 reloads its stack argument before returning it, and no source shape tried reproduces that
- Status: open
- Addresses: 0x000E17A0
- Checked: ghidra-mcp, matcher and reviewer of M4 batch 2 (2026-10-12)
- Evidence: The target is `mov eax,[esp+4]; mov [ecx+0x84],eax; mov eax,[esp+4]; ret 4`. The plain source `v = x; return x;` reuses eax and builds 13 bytes, a 58.8% match. Returning the member, a `const int&` parameter, a by-value struct parameter and a `volatile` member also failed. src/game/auto/000E.cpp keeps the plain form, parked as `source shape`.
- Next: try a different member type, a call or other code between the store and the return, or another flag set (F-0021 needs per-file flags).

## F-0077 Clearing low-byte flag bits with an all-ones upper mask builds `and al` and `or al`
- Status: open
- Addresses: 0x000F6E80
- Checked: ghidra-mcp, matcher and reviewer of M4 batch 2 (2026-10-12)
- Evidence: The target is `mov eax,[ecx+0x10c]; and al,0x2f; or al,0x20; mov [ecx+0x10c],eax`, which keeps bits 8 to 31. The two statements `flags &= 0xFFFFFF2F; flags |= 0x20;` match. The matcher reports that `(flags & 0x2f) | 0x20` builds `and eax,0xf`, which clears bits 8 to 31 and so is different code, not a compiler quirk. Whether the single statement `(flags & 0xFFFFFF2F) | 0x20` also matches, and whether the field at 0x10C is a 32-bit flags word, are untested.
- Next: compile the single-statement form, and check the other users of offset 0x10C when a namer reaches this class.

## F-0078 Two units hold a second `ret` that no function starts, so they cannot match as one function
- Status: open
- Addresses: 0x0015D6C0, 0x0015D6D0, 0x00165F20, 0x00165F30, 0x0014B490, 0x0014B4A0, 0x000120B0, 0x000120C0, 0x001A6E10, 0x001A6E20, 0x001A5DB0, 0x001A5DC0
- Checked: ghidra-mcp, matcher and reviewer of M4 batch 3 (2026-10-12)
- Evidence: Units come only from the `function` starts in config/symbols.txt (bodecomp/split.py), so a start that is missing there makes the unit before it too long. The unit 0x0015D6C0-0x0015D6E0 is `c3`, 15 bytes of `cc`, and a second `c3` at 0x0015D6D0. Ghidra sizes FUN_0015d6c0 at 1 byte with no references, and 0x0015D6D0 belongs to FUN_001235c0, whose jump at 0x00123633 reaches it, so it is a shared return of another function and not a function of its own. The unit 0x00165F20-0x00165F40 is a 16-byte body followed directly by `c3` at 0x00165F30. Ghidra sizes FUN_00165f20 at 16 bytes and has no function at 0x00165F30, but a data reference from the table slot 0x002EED88 points at it, so it is a 1-byte function that is missing. Night batch 1 of 2026-11-25 found a third unit, 0x0014B490-0x0014B4B0: a 16-byte constructor (`mov eax,ecx; mov [eax],0; mov [eax+4],0; ret`) followed by `8b 01 50 e8 98 7b fd ff 59 c3` at 0x0014B4A0 (`mov eax,[ecx]; push eax; call; pop ecx; ret`). Ghidra has no function at 0x0014B4A0 and no reference to it (disassemble_function, get_xrefs_to and read_memory by the matcher and the reviewer, 2026-11-25). The constructor source reaches 61.5% and is parked as `unclassified`. Night batch 2 of 2026-11-25 found two more. The unit of 0x000120B0 holds `8bc1 8b4c2408 8908 c20800` at 0x000120C0, and the unit of 0x001A6E10 holds `8b442404 894104 c20400` at 0x001A6E20, each followed by `cc` padding. Ghidra has no function and no reference at either address (read_memory by the matcher and the reviewer, 2026-11-25). The first functions are parked as `unclassified` at 59.3% and 61.5%. Night batch 3 of 2026-11-25 found one more: the unit of 0x001A5DB0 holds a 16-byte function, `cc` padding, and a jump-table function at 0x001A5DC0 (`8b442404 83f80d 0f87dc000000 ff2485...`). Ghidra has no function and no reference at 0x001A5DC0 (read_memory, disassemble_function and get_xrefs_to by the reviewer, 2026-11-25). 0x001A5DB0 is parked as `unclassified` at 59.3%. The first two units are parked as `unclassified` (5.9% and 94.1%). The reviewer's raw scan for non-padding bytes after a run of `cc` inside a unit found 15 units, including 0x000DC8F0, 0x00157EE0, 0x001BEEA0, 0x0020C750 and 0x00242660; that list is preliminary (ADR-0003), may include int3 bytes inside functions (F-0028, F-0075) or known gaps (F-0026), and cannot see the 0x00165F20 case, which has no `cc` run.
- Next: have a namer create a 1-byte function at 0x00165F30, regenerate the units and rematch 0x00165F20 from src/game/auto/0016.cpp. Decide how a unit should treat a return that another function jumps to, as at 0x0015D6D0. Check the 15 candidates in Ghidra and add a `bodecomp.gaps` check for code after padding inside a unit.

## F-0079 A target unit holds the relocation addend at a relocation site, not the absolute address
- Status: confirmed
- Addresses: 0x00302010
- Checked: test tests/test_trivial.py::test_global_names_the_relocation_target and test_global_named_in_the_target_table_gives_its_address (2026-10-12)
- Evidence: The delinked objects in build/target/units/ store, at each DIR32 relocation site, the offset from the relocation's symbol, and the symbol may be a name from build/target/symbols.tsv. The address a global access reads is therefore `match.target_value(symbol, literal, table)`, not the four bytes at the site. bodecomp.trivial.recognise takes that table as a fourth argument for this reason (M4 plan, Task 2 ruling).
- Revisit when: tools/delink.sh changes how it writes relocations.

## F-0080 The most common unclaimed small-function patterns are forwarding jumps, compiler thunks and vtable stores, and nine of the twelve compile from plain source
- Status: open
- Addresses: 0x00011020, 0x0003B2E0, 0x001E3560, 0x000111C0, 0x00011610, 0x000FC8D0, 0x000120A0, 0x0004A820, 0x00027B80, 0x00049E60, 0x00048E90, 0x00011220
- Checked: ghidra-mcp disassemble_function and get_xrefs_to on one function per pattern, and a trial source per pattern run through `bodecomp.match.check_source` (2026-10-12); ghidra-mcp disassemble_function on 0x00011220 (2026-10-12)
- Evidence: After M4 batch 3, `uv run python -m bodecomp.trivial shapes 12` lists the most common patterns among unclaimed units of 16 bytes or fewer; docs/m4-results.md, "Second gen_trivial pass", has the table. Ghidra confirms each reading but one. 0x00011020 is `JMP 0x000136d0`. 0x0003B2E0 is `SUB ECX,[ECX-4]` then `JMP 0x00036670`, and its only reference is data at 0x002E3934; 0x001E3560 is referenced only from data at 0x002F3DC0 and 0x002F52C8. 0x0004A820 is `MOV EAX,ECX`, `MOV [EAX],0x2e3cb8`, `RET`. 0x00049E60 is referenced as data from RegisterERFontClass and DynamicInit_ERFontClass. 0x00048E90 sits in a table at 0x002E3B30 that FUN_00049270 and FUN_00048dd0 reference. The correction: 0x000FC8D0 is `JMP [0x0035b7a4]`, and FUN_000fce00 writes 0x0035B7A4 at 0x000FCE6C, so the `ff25` pattern is a call through a function pointer the game sets at run time, not an import slot. One trial source per pattern matched under `check_source`: `g();` for `e9` and, with `g` a function pointer, for `ff25`; `return DAT_X;` or a string literal for `b8`; `f = a2; return this;` with two int arguments; `return p ? p[-1] : 0;`; a free function `a1->m();` for `8b4c2404e9`; and `delete this;` in a class whose virtual destructor is slot 5. The sentences below about the vtable stores describe the state before the 2026-10-12 resolver change in "Evidence (resolver)". The two vtable stores (`c701`, `8bc1c700`) match as a plain C++ destructor and constructor of a class whose first virtual function is named `FUN_` after the address in the target vtable's first slot (0x00011220 in 0x002E21BC, 0x0004A7A0 in 0x002E3CB8). With a virtual destructor or an unnamed first virtual instead, `check_source` reported that the function in that slot names no entry in config/symbols.txt. The `2b49fc` thunks were not tried, as the compiler makes them for virtual bases. The vtable-store form above is not plausible, though: Ghidra disassembles 0x00011220, slot 0 of 0x002E21BC, as `TEST [ESP+4],1`, a vtable store, a conditional call to 0x000136E0 and `RET 4`, which is VC71's scalar deleting destructor, so the real class declares a virtual destructor (ADR-0013). By a byte check, 189 of the 230 vtable-store functions have a slot 0 ending in `ret 4`. The honest form, `virtual ~S()`, failed because the compiled vtable's relocation names `??_E...`, which `Resolver.external` in `bodecomp/match.py` could not map to an address. The seven other writable shapes passed a reviewer and the second pass kept all 798 functions they cover (docs/m4-results.md).
- Evidence (resolver): `bodecomp.coff` reads a weak external's alias, and `bodecomp.match` follows `??_E` to the compiled `??_G` and compares that code with the original at the expected slot (test test_compiler_generated_slot_function_is_checked_against_the_original). The shapes `vtable-destructor` (`struct S { virtual ~S(); };` and an empty `S::~S()`) and `vtable-constructor` (`struct S { S(); virtual ~S() {} };` and an empty `S::S()`) passed a Sonnet reviewer, which confirmed in Ghidra that slot 0 of 0x002E21BC is 0x00011220 and slot 0 of 0x002E3CB8 is 0x0004A7A0, both scalar deleting destructors that call 0x000136E0. The third `generate` run kept 155 of 179 and 28 of 51 (docs/m4-results.md). A review found that the resolver checked an item only on its first visit within one relocation's chain, so a `??_G` that stores the vtable a second time was never compared; it now records the address each item was checked at and fails when a later reference expects another (test test_a_second_reference_to_a_checked_item_must_expect_the_same_address). `match --check` still reports 3305 matched after the change, so no current match depended on the gap.
- Evidence (issue #9): 0x00137AF0, one of the 47, writes the address 0x0035DC1C, which is not a vtable, and returns nothing. It matches as a method with no return value (F-0102). So the byte pattern of a vtable store also takes in a store of a data address.
- Next: find why the 47 other vtable-store functions do not match; the byte check above predicts 41 of them. Check first which of them store an address that is not a vtable, as 0x00137AF0 does.

## F-0081 Operator delete at 0x000136E0 is game code, not an SDK function
- Status: fixed (255aad4)
- Addresses: 0x000136E0, 0x00123040, 0x000136D0, 0x000136C0, 0x00011030
- Checked: ghidra-mcp disassemble_function and get_xrefs_to on 0x000136E0 (2026-10-12); `uv run python -m bodecomp.match --check` (2026-10-12)
- Evidence: Commit f117bb7 gave 0x000136E0 the tier `sdk` with evidence vc71-ddtor:0x00011220, but ADR-0005 defines `sdk` as a byte match against a library the XBE stamps, and no such match exists. Ghidra shows 0x000136E0 is `JMP 0x00123040` with 1063 references; operator new at 0x000136D0 calls FUN_00123060 with the size and 4, and 0x000136C0 is a second `JMP 0x00123040`, so both operators forward to the game's own allocator. A review raised the wrong tier. src/game/auto/000136E0.cpp defines `void operator delete(void* p)` as a call to FUN_00123040, VC71 compiles it to the same jump, and `names set` records it as `matched`. `match --check` reports 3306 matched, one more than before, and 0x00011030 in the same 64 KiB block still matches, as F-0073 concerns calls within one file only. `generate` still keeps 3227 of 3274, because a source outside src/game/trivial/ now claims 0x000136E0.

## F-0082 The C runtime's pure-virtual-call handler at 0x0021F734 had no function and no name
- Status: fixed (067ddf7)
- Addresses: 0x0021F734, 0x00224BC6, 0x003E0574, 0x002E38F4, 0x0021F748
- Checked: ghidra-mcp get_assembly_context, get_xrefs_to and get_functions (2026-11-14); `uv run python -m bodecomp.libmatch` (2026-11-14); relink run; ghidra-mcp disassemble_bytes dry run and get_xrefs_to on 0x0021F748 (2026-11-15)
- Evidence: Ghidra showed code at 0x0021F734 with 1,785 data references and no function: `MOV EAX,[0x003e0574]`, a call through that pointer when it is not zero, `PUSH 0x19`, `CALL 0x00224bc6`, `POP ECX`, `RET`. Slots 1 and 2 of the virtual base's vtable 0x002E38F4 point at it, so a class source that makes VC71 emit that vtable could not resolve `__purecall` (issue #2, spec/1-virtual-base-thunk-trial.md). `tools/create-functions.sh` created a 20-byte function there, and `bodecomp.libmatch` gave it the one name `__purecall` from `libcmt.lib`, member `obj\i386\purevirt.obj`, with tier `sdk`. Its unit runs from 0x0021F734 to 0x0021F758 and also holds 16 bytes of code from 0x0021F748 that no function covers: `MOV ECX,[ESP+0x4]`, `MOV EAX,[0x003e0574]`, `MOV [0x003e0574],ECX`, `RET`. That code stores a new handler pointer and returns the old one, and nothing references it. Its shape fits `_set_purecall_handler` of the same library member, which is a guess until `libmatch` names it. FUN_00224bc6, which `__purecall` calls, still has an automatic name.
- Revisit when: a compiled vtable's `__purecall` relocation does not resolve in `bodecomp.match`.

## F-0083 Slot 1 of class 2's main vtable, 0x0003C620, had no function and no target unit
- Status: fixed (067ddf7)
- Addresses: 0x0003C620, 0x002E3944, 0x0003C510
- Checked: ghidra-mcp get_assembly_context, get_xrefs_to and get_functions (2026-11-14); relink run
- Evidence: 0x0003C620 starts with `PUSH ESI`, `MOV ESI,ECX`, and its only reference is the vtable entry at 0x002E3944. Ghidra had no function there, so its code sat in the unit of FUN_0003c510 (0x0003C510 to 0x0003C6A0), whose body ends at 0x0003C60C. `tools/create-functions.sh` created FUN_0003c620 (120 bytes, body to 0x0003C697), and the delink of 2026-11-14 wrote `build/target/units/0003C620.obj`. Class 2 of the thunk trial needs this unit (issue #2).
- Revisit when: a class of the thunk trial finds another vtable slot that has no function.

## F-0084 Delinker v0.9.3 gives the same relocation tables and units as v0.9.2
- Status: confirmed
- Checked: `uv run python -m bodecomp.unitsplit --compare` (2026-11-14); relink run
- Evidence: Before the functions of F-0082 and F-0083 were created, `ExportUnits.java` exported all 19,795 units from copies of the project with Ghidra 12.2 and delinker v0.9.3, and the Python split of the v0.9.3 tables from the same state has 0 objects that differ from them. `relocs.tsv` from v0.9.3 equals the v0.9.2 file of 2026-10-12 line for line (129,203 relocations), and `symbols.tsv` differs only in the name at 0x000136E0, which commit 255aad4 changed. The export ran as six slices of the units list at the same time, each on its own copy of `ghidra/`, and took about 14 minutes, against 81 minutes for one process in October. After the delink, `bodecomp.relink` reports 0 mismatched bytes, 0 unresolved names and 0 unit problems on 19,797 units, and `config/functions.csv` is unchanged.
- Revisit when: the delinker extension is updated past v0.9.3.

## F-0085 The units list was older than symbols.txt for a month, and no check noticed
- Status: open
- Addresses: 0x000975F0, 0x000975FF, 0x0009BB20, 0x0009C6B0, 0x000ACB80, 0x000ADA10
- Checked: test (the function starts of `config/symbols.txt` at 742e585 against `build/target/units.txt`, 2026-11-14); relink run
- Evidence: `tools/delink.sh` cuts the units that `build/target/units.txt` lists and checks only that the file exists. `uv run python -m bodecomp.split` writes that file, and no tool runs it. The delink of 2026-10-12 used the list of 2026-10-11, from before commit 660a645 created 0x0009C6B0 and 0x000ADA10 and removed the start at 0x000975FF. Until 2026-11-14 the units 0x000975F0, 0x0009BB20 and 0x000ACB80 had the wrong ends, 0x0009C6B0 and 0x000ADA10 had no unit, and 0x000975FF had one. `bodecomp.relink` reported 0 unit problems all that time, because it compares the objects with the same list. No claimed function was in these units. The delink for issue #2 ran `bodecomp.split` first, so the units match `config/symbols.txt` at 067ddf7.
- Next: make `tools/delink.sh` write the units list itself, or make `bodecomp.relink` compare the list with `config/symbols.txt`.

## F-0086 A declared line cannot tell two constructors of one class apart
- Status: open
- Checked: test test_one_declared_name_with_two_addresses_is_a_problem
- Evidence: `bodecomp.match` resolves an external constructor or destructor through a `// declared: 0xADDRESS Class::Class` line (issue #3, `docs/WORKFLOW.md`, "Matching"). The line holds a name, and `decorated_prefixes` turns `Class::Class` into the one prefix `??0Class@@`, which every constructor of the class starts with. `scan` reports one name with two addresses as a problem, so a class with two constructors that are not matched cannot declare both. It is not checked whether a class of the thunk trial has two such constructors.
- Next: when a source calls two constructors of one class that are not matched, let the line take the decorated name of one constructor.

## F-0087 VC71 emits class 1's three vtordisp thunks with the original bytes
- Status: confirmed
- Addresses: 0x00047CE0, 0x00047CF0, 0x00047D00, 0x00047ED0, 0x000474C0, 0x00047520, 0x00047D10, 0x002E3A68, 0x002E3A78, 0x002E3AC8, 0x000359B0
- Checked: ghidra-mcp disassemble_bytes on 0x00047CE0, disassemble_function on 0x000474C0, 0x00047ED0 and 0x00047520, read_memory on 0x002E3A60, 0x002E3AC0 and 0x002E38F0 (2026-11-15); a test compile of a class 1 skeleton at `/O2 /G7 /arch:SSE`, run through `bodecomp.match.check_source` (2026-11-15); a test compile of two structs that hold such a pointer, in the review of pull request #15 (2026-11-15)
- Evidence: The probe of issue #4 compiled a scratch skeleton, `class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0`, with the constructor, the destructor and four overrides (`docs/thunk-trial-results.md`). VC71 emitted `2b49fc81e9ec000000e9` with a REL32 relocation to the deleting destructor for slot 0 of the virtual base's vtable, and `2b49fce9` with a REL32 relocation to the override for slots 1 and 2. These are the bytes at 0x00047CE0, 0x00047CF0 and 0x00047D00, and `/GX` does not change them. `check_source` reported the destructor 0x000474C0 and the overrides 0x00047520 and 0x00047D10 as `matched`. The destructor's match compares both vtables, the three thunks and the 40-byte deleting destructor 0x00047ED0 with the original. Three facts about the class came out of the compile. The destructor of the virtual base is inline in its class: with a declaration only, the built deleting destructor calls that destructor, and with an inline body it stores the vtable 0x002E38F4 as the original at 0x00047ED0 does. The class has only two members of its own, 8 bytes at +0x4C and a table of 12 pointers to member functions at +0x58, 12 bytes each (the donor's `Unk8003AA6CDraw unk54[12]`): with only these two declared, the virtual base is at +0xEC and the vbtable is `bcffffffa8000000` as at 0x002E3AC8, and two more `int` members at +0x48 and +0x54 moved the virtual base to +0xF4. So the gaps at +0x48 and +0x54 are padding. That VC71 aligns a pointer to a member function of this class to 8 bytes was a guess from the offsets of one test compile. A second test compile in the review of pull request #15 confirmed it for a member of a struct. For a class with a virtual base, `sizeof` of the pointer is 12, `__alignof` is 4 and an array has a stride of 12. In a struct, VC71 puts the member at a multiple of 8: at +0x8 after one `char`, and at +0x10 after an `int` and two `float` members. That explains the gap at +0x54. The cause of the gap at +0x48 is not tested. The overrides receive `this` as a pointer to the virtual base, so the 8-byte thunks hold no fixed offset.
- Revisit when: a class of the trial needs a thunk of another form.

## F-0088 The flags of ADR-0004 emit no exception-handling frame, and /GX emits the one of class 1's constructor
- Status: fixed (b842c44)
- Addresses: 0x00047D20, 0x002341B0, 0x002341CF, 0x002FA7B0, 0x002FA7B8, 0x000359B0, 0x000359C0, 0x002E38F4, 0x0021E485
- Checked: ghidra-mcp disassemble_function on 0x00047D20, disassemble_bytes on 0x002341A0, read_memory on 0x002FA7A0, get_xrefs_to on 0x002341CF and 0x002FA7B8 (2026-11-15); test compiles of the class 1 skeleton with and without `/GX`, run through `bodecomp.match.check_source` (2026-11-15); `bodecomp.match.run` on every claimed source with `/GX` added (2026-11-15)
- Evidence: The constructor 0x00047D20 starts with `PUSH -1`, `PUSH 0x2341cf`, and the read and the write of `FS:[0]`. 0x002341CF is `MOV EAX,0x2fa7b8`, `JMP 0x0021e485` (`___CxxFrameHandler`), in the unit of FUN_002341b0. The function info at 0x002FA7B8 has the magic 0x19930520, one state and the unwind table 0x002FA7B0, whose one entry names the funclet 0x002341B0. The funclet tests a flag at `[EBP-0x18]` and jumps to the virtual base's destructor 0x000359B0 with `this` + 0xEC. At `/O2 /G7 /arch:SSE` (ADR-0004) the skeleton's constructor has no frame, so its first byte differs. With `/GX` added, VC71 emits the frame, a `.text$x` section with the funclet and the handler, and a `.xdata$x` section with the unwind table and the function info. After the skeleton's constructor got a frame of the original's size (`sub esp,0xc`), the first difference moved to +0x18, the first byte after the frame setup, and the resolver returned 0x002341CF for the handler site. It compared the handler, the function info, the unwind table, the funclet, the destructor 0x000359B0, the vtable 0x002E38F4 and the deleting destructor 0x000359C0 with the original, and all were equal. With `/GX` added, every claimed source gives the row it has in `config/functions.csv`: 3306 matched and 3 parked. The target unit has no relocation and Ghidra has no reference for the function info address in the handler, and that did not matter, because the resolver reads the original bytes from the XBE. It is not checked whether `/EHa` gives the same bytes, and the exception model of the game's other libraries is not known.
- Evidence (fix): Class 1's constructor could not match without `/GX`, and the constructors of classes 2 and 3 start with the same frame (spec/1-virtual-base-thunk-trial.md). The maintainer chose on 2026-11-15 to add `/GX` to the default flags (ADR-0017). The test test_default_flags_emit_an_exception_handling_frame failed before the change, and `match --check` reports 3306 matched after it.
- Revisit when: a function's frame or state numbers differ in a way that another exception model (`/EHa`) would explain.

## F-0089 bodecomp.match could not match a function with an exception-handling frame
- Status: fixed (0858843)
- Addresses: 0x00047D20, 0x002341B0, 0x002341CE, 0x00047520, 0x00047CF0
- Checked: test test_handler_chain_equal_to_the_original_matches, test test_handler_chain_compares_the_funclet_bytes_after_a_label, test test_handler_frame_reads_except_list_as_the_value_zero, test test_a_vtordisp_thunk_is_not_the_definition_of_its_function; `uv run python -m bodecomp.match --check` (2026-11-15)
- Evidence: The probe of issue #4 found three gaps (F-0088). First, VC71 writes `FS:[0]` with a relocation to `__except_list`, and the resolver looked for that name in `config/symbols.txt`. `libcmt.lib` defines it in `obj\i386\exsup.obj` as an absolute symbol with the value 0, and the original has a plain 0 and no relocation, so the name now counts as 0. Second, VC71 puts a label symbol on the `RET` at the end of an unwind funclet (0x002341CE in the original). `Resolver.local_bytes` ended an item at any symbol, so that byte was in no compared item, and a funclet with another last instruction still matched. In code, an item now ends only at the next function symbol, which is the rule F-0001 gave `coff.function_bytes`. Third, VC71 names a vtordisp thunk after the function it jumps to (`?SetMode@Unk8003AA6C@@$4PPPPPPPM@A@AEXH@Z` beside `?SetMode@Unk8003AA6C@@UAEXH@Z`), so `defined_function` found two symbols for an override behind a thunk and reported an error. It now skips a name with `$` after the scope. `config/functions.csv` is unchanged at 3306 matched. The adjustor thunks of plain multiple inheritance have other name codes and are not handled.
- Revisit when: a function with a `try` block, or an override behind an adjustor thunk, goes through `bodecomp.match`.

## F-0090 A generated line claims a thunk or a deleting destructor, and class 1's four match through it
- Status: confirmed
- Addresses: 0x00047CE0, 0x00047CF0, 0x00047D00, 0x00047ED0, 0x00047EC0, 0x000474C0, 0x00047520
- Checked: test test_claimed_thunk_with_a_matched_target_is_matched, test test_claimed_thunk_whose_target_is_nonmatching_is_not_matched, test test_claim_that_the_check_never_reached_is_an_error, test test_generated_code_is_equal_when_a_later_check_that_reached_it_passed, test test_thunk_is_not_matched_when_a_function_further_along_its_jumps_is_not; test compiles of the class 1 skeleton of issue #4 with `generated` lines, run through `bodecomp.match.check_source` and `settle_jumps` (2026-11-15); `uv run python -m bodecomp.match --check` (2026-11-15)
- Evidence: Issue #5 added the line `// generated: 0xADDRESS` (`docs/WORKFLOW.md`, "Matching"). In a VC71 object at the default flags each vtordisp thunk is a COMDAT `.text` section of its own. The slot of the virtual base's vtable names it with a DIR32 relocation, and its REL32 jump names the override, or `??_E` for slot 0. So a claim's row comes from a check that a function with an address comment starts. With lines for 0x00047CE0, 0x00047CF0, 0x00047D00 and 0x00047ED0, the skeleton of F-0087 gives four `matched` rows, and a line for 0x00047EC0 gives `error`. With another body for the override 0x00047520, the row of 0x00047CF0 is `nonmatching` with "its jump target 0x00047520 is nonmatching". Without the line for 0x00047ED0, the row of 0x00047CE0 is `nonmatching` with "its jump target 0x00047ED0 is not claimed". `config/functions.csv` is unchanged at 3306 matched. The maintainer chose three limits on 2026-11-15. A thunk is any claimed function that ends in a jump, so a generated function with a tail jump also needs a matched target. One check fails as a whole, so a claimed function is `nonmatching` when an item beside it differs and no other check that reached it passed. The tool does not reject a line on an exception-handling funclet or handler, so that rule is in `docs/WORKFLOW.md` only. A `nonmatching` row of a claim has no score, because the resolver stops at an item's first difference. The review of pull request #14 found that `settle_jumps` read the status of each jump target once, before any row changed. A thunk that jumps to a claimed function that also ends in a jump kept `matched` when that function's own target was `nonmatching`. Commit 5c5a851 repeats the pass until no row changes. No class of the trial has such a chain.
- Revisit when: a claimed function with a tail jump cannot match because of its target's row, or a source claims a funclet or a handler.

## F-0091 Class 1 matches whole from real declarations and the shared header
- Status: confirmed
- Addresses: 0x00047D20, 0x000474C0, 0x00047ED0, 0x00047CE0, 0x00047CF0, 0x00047D00, 0x00047520, 0x00047D10, 0x00047540, 0x00047A10, 0x00047B70, 0x00047BD0, 0x00047C10, 0x00047C50, 0x00047C90, 0x002E3A78, 0x002E3A68, 0x002EC588, 0x002E38F4, 0x001249C0, 0x00047B30
- Checked: `uv run python -m bodecomp.match --check` (2026-11-15); ghidra-mcp disassemble_function on 0x00047D20, 0x00047540 and 0x001249C0, read_memory on the four vtables, get_xrefs_to on 0x00047B20, 0x00047CD0 and 0x00047EC0 (2026-11-15); the reviewer's test compiles of the other source forms through `check_source` (2026-11-15); in the review of pull request #15, ghidra-mcp disassemble_function on slots 1 to 16 of 0x002EC588 and on 0x00047B30 and 0x00047BD0, and get_xrefs_to on 0x00047B30 (2026-11-15)
- Evidence: Issue #6 wrote `src/game/auto/UnkTargetBase.h` and `src/game/auto/00047D20.cpp`. The 10 required functions of class 1 are `matched`, 2,031 bytes, and the reviewer's verdict is clean (`docs/thunk-trial-results.md`). The constructor matched on the matcher's first compile, with its exception-handling frame. It clears 0x90 bytes at +0x58 and stores 12-byte pointers to member functions with a stride of 12: entries 0 to 6 and 8 to 11, entry 9 before entry 8, and entry 7 stays zero. The targets are 0x00047B70, 0x00047BD0, 0x00047C10, 0x00047C50 (twice), 0x00047C90, and 0x00047B70 for the rest. The stride is the size of the pointer, and the table starts at a multiple of 8, as F-0087 describes. The base constructor 0x001249C0 agrees with the header's layout: 12 bytes at +0x4, a pointer at +0x10, the member that 0x00137AF0 builds at +0x18, `flags` at +0x1C with the value 0x16, floats from +0x24, the player at +0x3C and bytes at +0x40 and +0x41. Three source forms decide a match: `IsBuildMode()` is defined in `Unk8003AA6C` and not in the virtual base, 0x00047A10 tests `draw[mode] == 0` first, and F-0092 gives the two of 0x00047540. One form does not decide it: 0x00047A10 matches with `&EVec2(...)` and with named `EVec2` locals, and the source keeps `&EVec2(...)`, the donor's form. 0x00047B20, 0x00047CD0 and 0x00047EC0 have no reference and are in neither vtable, so they stay in `src/game/trivial/`. The review of pull request #15 changed two things. The header declared slots 4, 5, 7 to 11 and 13 to 15 of `UnkTargetBase` with no parameters, and each of these functions ends in `ret 4`, `ret 8` or `ret 0xc`. Slots 8 and 12 return a value. The header now gives each slot the parameter count of its function. The class also declares 0x00047B30, a member function with no reference: it reads the player at +0x3C, and 0x00047BD0 holds its body inline. The 11 stand-in classes of the source had names such as `EDialogs`, which read as engine names, and only `EController` is a name from the donor. They are now `Dialogs_00047D20` and the like. The member names other than `flags` and `player`, the parameter types of the base slots other than slot 2, and the role words of the stand-in classes are guesses (F-0069).
- Revisit when: class 2 or class 3 needs another layout of `UnkTargetBase` or another signature of a base slot.

## F-0092 0x00047540 was parked as a register tie, and two source-shape differences were the cause
- Status: confirmed
- Addresses: 0x00047540, 0x0004779E, 0x0004780F, 0x001249C0, 0x00124980, 0x00124940
- Checked: ghidra-mcp disassemble_function on 0x00047540, search_instructions for `MOV EBP, 0x1` (2026-11-15); test compiles of variants of the class source by the lead, and the reviewer's `check_source` runs of the other forms (2026-11-15); in the review of pull request #15, ghidra-mcp disassemble_function on 0x00124980 and 0x00124940, and one more variant through `bodecomp.match --check` (2026-11-15)
- Evidence: The matcher parked 0x00047540 (1231 bytes) at 16.2% after five attempts. VC71 built 1251 bytes, kept the controller in EBX, and used EBP for a value held across two calls and for the constant 1. The original never uses EBP there. The original loads the constant 1 into EBP in other functions (22 times in the first 232,363 instructions, where the search stopped at its limit), so a compiler flag is not the cause. A diff of the two instruction lists with the register names blurred showed two differences that are not registers. First, the block that sends message 0x24 sits at 0x0004779E, after the block that sends 0xD. With `if (pause)` after the `if` and `else` that set `pause`, as in the GameCube donor, VC71 gives that order. Second, the flag test at 0x0004780F is `mov ecx,[edi+0x1c]`, `shr ecx,1`, `test cl,1`, where VC71 built `test byte ptr [edi+0x1c],2`. With the read through `bool Flag1() const { return (flags >> 1) & 1; }`, VC71 gives the original test, and the register layout follows: 1231 bytes and no EBP. That this accessor caused the change of the layout is evidence from the compiles, because nothing else differed between the two builds. A direct read of `flags`, a 1-bit bitfield read directly and an accessor that returns `int` all give the short test and the EBP layout. The review of pull request #15 added two facts. The expression `(other->flags >> 1) & 1` in the function, without the accessor, gives 1243 bytes and 15.0%. The base class has the same test: 0x00124980 tests bit 1 with `shr eax,1`, `test al,1`, and 0x00124940 tests bit 2 with `shr eax,2`, `test al,1` and bit 6 with `test byte ptr [edi+0x1c],0x40`. So the original reads bits 1 and 2 through another source form than bit 6. The base constructor stores 0x16 to +0x1C with one move, so `flags` is a plain `unsigned int` in the header.
- Revisit when: a function is parked as `register tie` and no diff of the instruction lists with blurred register names was made.

## F-0093 Class 2 matches whole from real declarations and the shared header
- Status: confirmed
- Addresses: 0x0003B940, 0x0003B230, 0x0003B360, 0x0003B2D0, 0x0003B2E0, 0x0003B2F0, 0x00036670, 0x0003B300, 0x0003C620, 0x0003B2C0, 0x00036570, 0x00038D00, 0x000365B0, 0x0003B8D0, 0x002E3940, 0x002E3930, 0x002EC588, 0x002F9FD8, 0x00233AC8, 0x00233AD6, 0x00035E50, 0x00035E60, 0x00142B90, 0x00233B40
- Checked: `uv run python -m bodecomp.match --check` (2026-11-15); ghidra-mcp read_memory on 0x002E3930 and 0x002EC588 by the lead, disassemble_function on the 13 required addresses and read_memory on 0x002F9FD8 and its funclets by the matcher and the reviewer (2026-11-15); the reviewer's compiles of the other source forms through `bodecomp.match` in a scratch root (2026-11-15); GC repo d8483a6 for the `EVec3` constructors; in the review of pull request #16, ghidra-mcp read_memory on 0x002E3930, disassemble_function on 0x00036670, 0x00038D00 and 0x0003C620, and test compiles of the donor's source forms from GC repo d8483a6 through `bodecomp.match` (2026-11-15)
- Evidence: Issue #7 wrote `src/game/auto/0003B940.cpp`. The 13 required functions of class 2 are `matched`, 1,990 bytes, and the reviewer's verdict is clean (`docs/thunk-trial-results.md`). The main vtable 0x002E3940 overrides slots 1 (0x0003C620), 2 (0x0003B2C0), 3 (0x00036570) and 6 (0x00038D00) of `UnkTargetBase` and adds slot 17 (0x000365B0). The vbtable is `bcffffffa8010000`, so the virtual base is at +0x1EC. The class's own members start at +0x50 with a table of 7 pointers to member functions, 12 bytes each, and nothing sits at +0x4C. The constructor matched with its exception-handling frame (F-0095). The destructor 0x0003B230 has three unwind states. Its funclets 0x00233AC8 and 0x00233AD6 jump to two different thunks, 0x00035E50 with `this` + 0x164 and 0x00035E60 with `this` + 0x1B0, and each thunk is a jump to 0x00142B90. So the lists at +0x164 and +0x1B0 are two types with one shared clear function, where the donor has one type. With one type for both, the row is `nonmatching` at 97.2% with "item at +0x0 is expected at 0x00035E50 and 0x00035E60". Three more source forms decide a match, and the reviewer compiled the other form of each. The constructor stores the player before `unkBC = EVec3(0.0f)` (the other order gives 92.9%). 0x00038D00 returns from the success block first (the other order gives 89.6%). 0x00036670 is in F-0094. The header changed in three places, and class 1's 10 rows stay `matched`. `EVec3` got the donor's two constructors, `EVec3() {}` and `explicit EVec3(float value) { x = y = z = value; }`: the reviewer's compile with three plain stores in place of `EVec3(0.0f)` gave 13.4% on the constructor, with a `.text$x` item that differs from 0x00233B40, and the cause of that is not examined. `UnkTargetBase` declares 0x00124680 and has the inline `SetFlags` of F-0094. No layout and no signature of a base slot changed, so the revisit condition of F-0091 did not come up. 0x0003B2C0 and 0x0003B300 moved from `src/game/trivial/0003.cpp` to the class source. Guesses (F-0069): the member names, `pad198` and the `EVec3` at +0x1A4, which the constructor never writes, the role words and the dummy slots of the stand-in classes (only the slot index and the parameter count of a called slot are read from the binary), the dummy first virtual base of `Part_0003B940` and `Node_0003B940`, and the return types of the five handler functions. The matcher's statement that each member from the donor's `unk94` on sits 0x1C higher on the Xbox is not checked by the lead. The review of pull request #16 compiled the donor's form of each function, which the matcher and the reviewer had not done. Five donor forms match, and the source now has them. 0x0003C620 is the donor's `switch (mode)` with the cases 0 to 7 and 9, where the pull request had an `if` chain on a local copy of `mode` (`m >= 0`, `m > 7`, `m == 9`), with the claim that the order of its branches decides the match. 0x00036570 sends `player == 0 ? 0x15 : 0x16`, where the pull request had `(player != 0) + 0x15`. The tile at +0x1C0 is one 8-byte struct, and 0x00038D00 copies it with one assignment. The 17 words from +0x118 are 17 members and not an array: the constructor stores +0x14C before +0x148. 0x00038D00 tests `object && object->vfn123()` in one `if`. Four donor forms do not match on the Xbox, so the source keeps its own form of each: an inline `Common()` for the three calls that `SetMode` repeats (54.7%, 364 bytes against 352), `IsBuildMode` as a member of the virtual base (9.0% on 0x00038D00), the constructor's statements in the donor's order (93.4%), and one sound call after the `if` in 0x00038D00 (84.7%). A direct `flags & 2` test in 0x0003C620 gives 34.2%, so the function needs the `Flag1` accessor of F-0092.
- Revisit when: class 3 needs another layout of `UnkTargetBase` or another signature of a base slot, or a donor or Ghidra fact names the two list classes.

## F-0094 0x00036670 was parked as a scheduling difference, and an inline helper of the base class was the cause
- Status: confirmed
- Addresses: 0x00036670, 0x0003B2E0, 0x000366D2, 0x00124680, 0x000365B0, 0x00017CD0
- Checked: ghidra-mcp disassemble_function on 0x00036670 and 0x00124680 (2026-11-15); test compiles of variants of the class source by the lead through `bodecomp.match`, and the reviewer's compiles of the other forms (2026-11-15); in the review of pull request #16, disassemble_function on both addresses again and two test compiles (2026-11-15); `uv run python -m bodecomp.match --check` and ghidra-mcp get_functions on 0x00124680 in the batch of issue #32 (2026-11-17)
- Evidence: The matcher parked `SetMode` 0x00036670 (348 bytes with its jump table) at 94.8% after six source forms, and the thunk 0x0003B2E0 waited on it. A diff of the instruction lists with blurred register names showed the same instructions in another order, in case 0 only. The original at 0x000366D2 has `push 1`, the store of 0 to +0xA4, `mov edx,[edi]`, `push 2`, `mov ecx,edi`, `call [edx+0x24]` and then `or dword ptr [edi+0x1c],2`. VC71 built the vtable load first and the store last. 0x00124680 is a member function of `UnkTargetBase` that is not virtual and has 30 callers. It calls slot 9 with its two arguments, sets or clears `flags` by the second argument, and then calls itself on each child. Case 0 holds the first two steps with the constants 2 and 1, and no loop. With these two steps in an inline member of the base, `void SetFlags(unsigned int bits, bool set)`, and `unkA4 = 0; SetFlags(2, true);` in case 0, VC71 gives the original order and the function matches. Two other forms do not: `FUN_00017CD0(2, 1); flags |= 2;` gives 27.8%, and `FUN_00017CD0(2, 1); Unk80026864::FUN_000365B0(2, true);`, the matcher's best form, gives 94.8%. That the helper caused the order is evidence from the compiles, because nothing else differed between the builds. That the original source had such a helper is a guess: its only evidence is the match. Case 0 is not a call of 0x00124680, because it has no loop. The batch of issue #32 matched 0x00124680 at 100% as `SetFlags(bits, set)` followed by a loop over the child list at +4 (the child at +0 of a node, the next node at +8) that calls 0x00124680 on each child. That match needs the second parameter of slot 9 as `bool`: with `int`, VC71 adds `movzx ecx,bl` before the push and gives 41.4%. The original pushes EBX and its callee tests only the low byte. The other cases of `SetMode` call 0x00124680, and 0x000365B0 (slot 17) holds the same set-or-clear without the call of slot 9. The review of pull request #16 added two facts. The donor's statements for case 0, `unkA4 = newMode; FUN_00017CD0(2, 1); flags |= 2;`, give the same 27.8%. With `SetFlags` as a member of `Unk80026864` and not of the base, the function matches too, so the match does not decide which class owns the helper. The header keeps it in the base because of 0x00124680.
- Revisit when: a function is parked as `scheduling` and nobody looked for a function in the binary that holds the same statements.

## F-0095 The constructor 0x0003B940 has one unwind state because 0x0003B8D0 is defined in the same source
- Status: confirmed
- Addresses: 0x0003B940, 0x0003B8D0, 0x002FA074, 0x002FA06C, 0x00233B40, 0x00308C9C, 0x003DD554, 0x003DD52C, 0x00038A70
- Checked: ghidra-mcp read_memory on 0x002FA074 and 0x002FA06C, disassemble_function on 0x0003B8D0 (2026-11-15); test compiles by the matcher, the lead and the reviewer through `bodecomp.match` (2026-11-15)
- Evidence: The function info of the constructor at 0x002FA074 has one state, and its unwind table 0x002FA06C has the one entry for the virtual base's funclet 0x00233B40. The constructor calls 0x0003B8D0 first. With 0x0003B8D0 declared only, VC71 at `/GX` adds unwind states for the base and the list members: the `.xdata$x` section of the constructor is 0x3C bytes, against 0x24 bytes in the forms that match. Three forms give the one state. The matcher declared the function with `throw()`. The lead defined it in the source before the constructor, which is the order of the addresses. The reviewer moved the definition after the constructor, and the constructor still matched. So VC71 takes a definition anywhere in the translation unit as proof that the function cannot throw, and it did not inline the call. The source keeps the definition and has no `throw()`. 0x0003B8D0 is `matched` as an extra, 112 bytes: it copies 40 bytes from 0x00308C9C to 0x003DD554 and stores nine function addresses to 0x003DD52C and on (0x0003A0E0, 0x00038320, 0x00038500, 0x00038640, 0x00038710, 0x0003A180, 0x000387E0, 0x0003B8B0 and the thunk 0x00038A70). It has one caller. The source has it as a static member of the class, and a free function matches too, so its owner is a guess. With the function declared only and no `throw()`, the row shows 21.6% with "relocation at +0x3 ... is not fully backed by file data". That message comes from the resolver and not from a byte difference in the constructor's code.
- Revisit when: a constructor's unwind states differ from the original's and one of its callees is declared only.

## F-0096 The first rebuild on Ghidra 12.2 rejected 2 starts and split 1 function, and the rebuilt project has 2 functions without a stray pointer
- Status: fixed (88a9b95)
- Addresses: 0x0009C6B0, 0x0009E22B, 0x0009E22C, 0x00223652, 0x00220A24, 0x000975F0, 0x000975FF, 0x001747F0, 0x0017496C
- Checked: ghidra-mcp on the Mac project and on a WSL 2 rebuild (2026-11-15); a scratch import of `orig/default.xbe` on the Mac with Ghidra 12.2, `CreateFunctions.java` before and after the fix on copies of the same import, `sync apply` and `sync check` on the fixed copy through a second server, and a size comparison of every function with the Mac project (2026-11-15)
- Evidence: The first full `tools/rebuild-ghidra.sh` on 12.2 ran in WSL 2 and gave `functions created 11558, already present 10174, rejected 2, total 21869`. The scratch import on the Mac gave the same line, so the cause is not the machine. 0x0009C6B0 was `bad-instruction 0009e22b`: the import puts a pointer `DAT_0009e22c` with no references at 0x0009E22C, inside the `call` at 0x0009E22B, and the Mac project still has it, with no instructions from 0x0009E22B to 0x0009E287, because M2b Task 7 created the function by hand (F-0065). 0x00223652 (`__fast_exit`) was `missing`: the 12.2 analysis put it into the body of `FUN_00220a24` as a second chunk, because two `JMP` and eight `Jcc` reach it, and the script counted a listed start inside any function as present. The import also splits `GetLoadBarVariable` 0x000975F0 at 0x000975FF again (F-0040), which `sync check` reports as not in `symbols.txt`. In `starts` mode the script now creates a listed start that sits at an instruction in another function's body, clears data with no references in the range that `clearStrayCode` clears, and removes each function that the list does not hold. On a copy of the same import it gave `functions created 11561, already present 10173, removed 1, rejected 0, total 21870`, and `sync check` gave 0, 0 and 0. Every function has the size of the Mac project except two, where the Mac project has a pointer with no references inside the code: 0x0009C6B0 is 9,207 bytes in the rebuild and 9,114 on the Mac, and `AllocXBoxTextureData` 0x001747F0 is 384 bytes in the rebuild and 380 on the Mac, where the address-table analysis put `DAT_0017496c` over its last `pop ebx; ret 4` (bookmark "Address table[9] created"). The rebuild's sizes are the real ones (evidence: the instructions in the rebuilt project). `config/symbols.txt` still holds the Mac sizes, and the relocations of these two functions, and no others, differ from the Mac's `build/target/relocs.tsv` (evidence: the delink of the scratch rebuild, F-0097). `ExportStringRefs.java` on the scratch rebuild gives 3560 string references in 813 functions, against 3522 in 812 on the Mac, and all 38 more are references from 0x0009C6B0 to strings of the build menu such as `wall_tool_name` (evidence: a diff of the two `strings.tsv` files, 2026-11-15). That the analysis made the pointer at 0x0009E22C from the call's operand is a guess.
- Revisit when: the Mac project is rebuilt, or another rebuild rejects a start, removes a function or gives a size that differs from `symbols.txt`.

## F-0097 The delink of a rebuilt project stopped on a duplicate name, because the exporter picks any one of the mangled labels at an address
- Status: fixed (24ccd93)
- Addresses: 0x0021E41E, 0x0021E425, 0x0021E42C
- Checked: `tools/delink.sh` in WSL 2 on the rebuild of F-0096 (2026-11-15); `ExportTextObject.java` and `ExportDelinkTables.java` on the scratch rebuild of F-0096 on the Mac, before and after the fix, then `bodecomp.unitsplit`, `bodecomp.relink` and `bodecomp.match --check` on its units; a headless script that lists every symbol at an address, on the scratch rebuild and on a copy of the Mac project (2026-11-15)
- Evidence: In WSL 2, `ExportTextObject.java` failed with `COFF export failed: Duplicate symbol name '?_CallMemberFunction2@@YGXPAX00H@Z' (2 instances)`, and the scratch rebuild on the Mac gave the same error. Both projects hold the same symbols at the two equal 7-byte functions 0x0021E425 and 0x0021E42C: a primary `FID_conflict:` name from `config/symbols.txt`, and the Function ID labels `?_CallMemberFunction1@@YGXPAX00@Z` and `?_CallMemberFunction2@@YGXPAX00H@Z`. These are the only two addresses in the Mac project with more than one mangled name. The delinker's MSVC preference (`SymbolPreference.pickMsvc`) takes `findAny` of the mangled names in a `HashSet`, so its choice follows the symbol IDs of the project: the Mac delink of 2026-11-14 named 0x0021E425 `?_CallMemberFunction2@@YGXPAX00H@Z` and 0x0021E42C `?_CallMemberFunction1@@YGXPAX00@Z`, and the rebuild gave the second name to both. Both export scripts now remove, in memory only, the labels with a mangled name that are not primary at each address that holds more than one, so the exporter takes the primary name. On the scratch rebuild this removed 4 labels, the delink wrote 19,797 units with 129,369 relocations and 89,171 symbols, and `bodecomp.relink` gave 0 mismatched bytes, 0 unresolved names and 0 unit problems. `bodecomp.match --check` on those units gave 3327 matched, 0 nonmatching and 3 parked, as on the Mac. The relocations differ from the Mac's `build/target/relocs.tsv` only from 0x0009C6B3 to 0x0009EAA6 and at 0x0017496C, the two functions of F-0096. `ExportUnits.java` got the same change and is not run.
- Revisit when: a delink names a function differently from the delink before it, or the delinker changes `SymbolPreference`.

## F-0098 A declared override resolved to the address of the base's slot, and a declared line now gives it its own
- Status: fixed (fa1afc6)
- Addresses: 0x000A8720, 0x000ADA10, 0x000A8CC0, 0x000A9CF0, 0x000AAEC0, 0x00124940, 0x00124980, 0x00017C90, 0x00017CB0, 0x00017CC0, 0x000A80B0, 0x000ACA40, 0x002E7578
- Checked: test test_call_to_a_declared_override_resolves_to_the_stated_address, test test_override_without_a_declared_line_resolves_to_its_base_slot, test test_declared_override_gives_no_address_to_the_base_slot, test test_declared_line_takes_no_free_function_or_operator, test test_declared_member_name_is_made_of_identifiers (b239523); the matcher's and the reviewer's compiles of the class 3 source without the five bodies (2026-11-15); `uv run python -m bodecomp.match --check` (2026-11-15)
- Evidence: Class 3 overrides slots 1, 2, 6, 7 and 8 of `UnkTargetBase` with five large functions that the spec declares only. An override keeps the name of the base's slot, for example `S_000A80B0::FUN_00124940`, and `Resolver.external` resolved its `FUN_` leaf to the base function's address 0x00124940. The constructor and the destructor store the main vtable, so with the five declared only they were `nonmatching` at 97.9% and 97.1% with "relocation at +0x5B: .rdata+0x4 points elsewhere", which is slot 1. The matcher made them match with five empty bodies marked `// parked: unclassified`. The reviewer failed the bodies, because nobody had tried to match them and they raised the parked count from 3 to 8. The maintainer chose on 2026-11-15 to let a `declared` line take an override, which changes R1 of the plan in `spec/1-virtual-base-thunk-trial.md`. `read_declared` now accepts a member function name that is not an operator. The review of the pull request found that fa1afc6 also accepted `Foo::operator=`, `Foo::~Bar`, `::Bar` and `Foo::Bar extra`, so since b239523 each part of the name must be a C++ identifier. The resolver already read a `declared` line before the `FUN_` leaf. The class source has five `declared` lines in place of the bodies, the 9 required rows stay `matched`, and `match --check` reports 3336 matched and 3 parked. The tool cannot tell an override from another member function, so the rule that the line is for an override is in `docs/WORKFLOW.md` only. One line gives its address to every overload of the name.
- Revisit when: a source needs a `declared` line for two overloads of one member function, or for a member function that is not an override.

## F-0099 Class 3 matches whole from real declarations and the shared header
- Status: confirmed
- Addresses: 0x000A80B0, 0x000ACA40, 0x000ACB50, 0x000ACA10, 0x000ACA20, 0x000ACA30, 0x000A8180, 0x000A8220, 0x000A8C40, 0x000A82C0, 0x002E7578, 0x002E7568, 0x002E75C4, 0x0008FB70
- Checked: `uv run python -m bodecomp.match --check` (2026-11-15); ghidra-mcp read_memory on 0x002E7568 and disassemble_function on 0x000A80B0, 0x000ACA40, 0x000ACB50, 0x000A8180, 0x000A8220, 0x000A8C40 and 0x0008FB70 by the lead, and on the 9 required addresses, the vtables and the menu functions by the matcher and the reviewer (2026-11-15); the reviewer's compiles of the other source forms (2026-11-15); the symbols of `build/match/src/game/auto/000A80B0.obj` and ghidra-mcp get_xrefs_to on 0x0008FB70 by the review of the pull request and by the lead (2026-11-15)
- Evidence: Issue #8 wrote `src/game/auto/000A80B0.cpp`, and the shared header did not change. The 9 required functions are `matched`, 823 bytes, and the reviewer's verdict on them is clean (`docs/thunk-trial-results.md`). The main vtable 0x002E7578 has 19 slots. Slots 0 to 16 are those of `UnkTargetBase`, with overrides in slots 0, 1, 2, 6, 7 and 8, and slots 17 (InitPauseMenu 0x000A82C0) and 18 (0x000A8C40) are new. The virtual-base vtable 0x002E7568 holds the three thunks, and the vbtable 0x002E75C4 is `bcffffff68250000`, so the virtual base is at +0x25AC. The constructor matched with its exception-handling frame once the vtable resolved (F-0098). The members are the buy menu at +0x6C and the build menu at +0x1288 (F-0100), pointers at +0x24AC, +0x24B4 and +0x24C4, and ints at +0x24BC and +0x24CC. The reviewer compiled the other form of each source form that decides a match. `SetMode` 0x000A8180 is a `switch (newMode)` with the cases 8, 10 and 11: `newMode == 8 || newMode == 10 || newMode == 11` gives 97.3%, and `newMode == 8 || (newMode >= 10 && newMode <= 11)` gives 98.6%. Its last branch compares the pause mode with 12 before it tests 0, and without that compare the function gives 81.8% to 83.8%. A `switch` on the pause mode with the cases 4, 5, 12 and 0 gives 29.1%. 0x000A8220 calls slot 18, slot 17 and then `SetMode(8)`, and the other orders give 44.6% to 98.6%. 0x000A8C40 needs `if (p) { delete p; p = 0; }` for +0x24AC (88.7% without the `if`), the `if` around the call on +0x24B4 (12.1% without it), and `delete p; p = 0;` for +0x24C4. The destructor's body is the call of 0x000A8C40, and an empty body gives 45.7%. A `generated` line for 0x0008FB70 gives `error`. An `error` row shows only that no check reached the claim, so two other facts show that the object does not emit that function: `build/match/src/game/auto/000A80B0.obj` defines no `??_D` symbol, and Ghidra has 0 references to 0x0008FB70. That it is the vbase destructor `??_D` stays a guess. Guesses (F-0069): the class name and the member names, the types behind +0x24AC, +0x24B4 and +0x24C4, the stand-in classes `Owned_000A80B0`, `Counted_000A80B0` and `Flash_000A80B0`, `FUN_000A2A50` as a free function, the parameter types of the menu methods, and the nested `if` of the last branch of `SetMode`, where `unk24BC != 12 && unk24BC == 0` gives the same bytes.
- Revisit when: a string names the pause screen class, or the callers batch needs another layout of the class.

## F-0100 The buy and build menus derive from the class of 0x00145A00, and their sizes rest on the gaps in the pause screen
- Status: open
- Addresses: 0x00145A00, 0x00145B00, 0x002ED510, 0x001565A0, 0x000A1B00, 0x0009F540, 0x000A0DD0, 0x0009BAB0, 0x000A1C00, 0x0009EAB0, 0x0009BB20, 0x00053DD0, 0x000329D0, 0x0015A3F0, 0x00020EF0
- Checked: ghidra-mcp disassemble_function on 0x00145A00, 0x000A1B00 and 0x000A0DD0, and get_xrefs_to on 0x00145A00 and 0x00145B00 by the lead; disassemble_function on the menu constructors, destructors and update functions by the matcher and the reviewer (2026-11-15)
- Evidence: 0x00145A00 calls the base constructor 0x001249C0, stores the vtable 0x002ED510, builds two members with 0x001565A0 at +0xA4 and +0xCC, and ends in `ret 0x14`, so it takes five arguments. The buy menu's constructor 0x000A1B00 and the build menu's constructor 0x0009F540 call it, and their destructors 0x000A0DD0 and 0x0009BAB0 call 0x00145B00. The first member of the buy menu is an array of 9 items of 0x19C bytes at +0xF4. The class 3 source declares `S_00145A00 : UnkTargetBase` with a size of 0xF4. The pause screen puts the buy menu at +0x6C, the build menu at +0x1288 and its next member at +0x24AC, so the gaps are 0x121C and 0x1224. The largest offsets that the menus' own functions use are a byte at +0x1218 (0x000A1C00) and a byte at +0x1220 (0x0009EAB0, 0x0009BB20). These prove only sizes of at least 0x1219 and 0x1221. The source takes the gaps as the sizes, which fits 4-byte alignment, and whether the last 3 bytes of each gap belong to the menu is a guess. The size 0xF4 of `S_00145A00` and 0x28 bytes for each member that 0x001565A0 builds are guesses from the offsets. 0x00145A00 has 8 calls from 6 functions: the two menu constructors, 0x00053DD0 of the callers batch (issue #9), 0x000329D0, 0x0015A3F0 and HandleCASMessage 0x00020EF0. 0x00145B00 has 14 calls from 13 functions. The callers batch (issue #9) moved `S_00145A00` to `src/game/auto/UnkTargetBase.h` for 0x00053DD0, which derives from it. The header now declares the 31 slots of the vtable 0x002ED510: 7 overrides of `UnkTargetBase` with `declared` lines and 14 new slots, with the parameter counts of each `ret N` (F-0101). 0x00053DD0 puts its virtual base at +0x320 and does not prove the size 0xF4.
- Next: confirm the size of `S_00145A00` from a class that holds it as a member or allocates it with `operator new`.

## F-0101 The callers batch matches 18 of its 20 functions from real declarations and the shared header
- Status: confirmed
- Addresses: 0x00053DD0, 0x000BD710, 0x00097300, 0x000AF6F0, 0x000E31C0, 0x00097AC0, 0x00026140, 0x00026240, 0x000B7340, 0x000929C0, 0x000E3200, 0x000F0DE0, 0x0007CFB0, 0x00017D10, 0x000E3280, 0x000BD910, 0x00139550, 0x00096220, 0x000AF910, 0x0005A4E0, 0x00053EE0, 0x000BDAF0, 0x00053D00, 0x000BD8D0, 0x000AF780, 0x00026190, 0x00026290, 0x00124810, 0x002ED510, 0x002EA260
- Checked: `uv run python -m bodecomp.match --check` (2026-11-15); ghidra-mcp disassemble_function, read_memory and get_xrefs_to on the 20 functions, the vtables and the callees by the matcher and the reviewer (2026-11-15); the reviewer's compiles of the other source forms (2026-11-15)
- Evidence: Issue #9 wrote 18 sources in `src/game/auto/`, one per class, and changed the shared header. 18 of the 20 functions are `matched`, 1,737 bytes. 0x000BD710 (F-0107) and 0x00017D10 (F-0108) are parked. The deleting destructors 0x00053EE0 and 0x000BDAF0 of the two per-player screens match through `generated` lines, and so do the thunks 0x00053D00 and 0x000BD8D0 that jump to them. The thunks 0x00053D10, 0x00053D20, 0x000BD8E0 and 0x000BD8F0 are not claimed, because their targets are declared only. The header gained the donor's `EVec2(float)`, `UnkTargetBase::FUN_00124810`, which calls slot 14 for each child, `UnkTargetText` for the member at +0x18 (F-0102) and `S_00145A00` (F-0100). Classes 1 to 3 stay `matched`. The matcher parked 0x000E3280 as `scheduling` at 67.0% after about 30 forms of four `float` members, and the reviewer matched it with two `EVec2` members, because the donor's `EVec2(float)` stores y first. The constructors of 0x000E3280 and 0x000F0DE0 do not call 0x000E31C0 but repeat its stores, so their base class `Dialog_000E31C0` has an inline constructor, and 0x000E31C0 is an out-of-line copy of it. Each of the two sources declares the base, and the reviewer showed that one shared declaration gives the same bytes. The vtable 0x002EA260 of that base overrides only slot 0. 0x0005A4E0 matches with one list class, where the matcher had two. Guesses (F-0069): every class name and member name, the sizes of the `pad` arrays, the stand-in classes, the 8 parameter types of the constructor that 0x000BD710 calls, and `unsigned short*` for the text member.
- Revisit when: a later batch needs another layout of one of these classes, or a string or the donor names one of them.

## F-0102 0x00137AF0 writes the address of a data item and is not a vtable store
- Status: confirmed
- Addresses: 0x00137AF0, 0x001249C0, 0x0035DC1C
- Checked: ghidra-mcp disassemble_function on 0x00137AF0 and 0x001249C0 by the matcher (2026-11-15); `uv run python -m bodecomp.match --check` (2026-11-15)
- Evidence: 0x00137AF0 is `MOV dword ptr [ECX],0x35dc1c`, `RET`, 7 bytes. 0x0035DC1C is in the uninitialized data, not a vtable. The constructor 0x001249C0 of `UnkTargetBase` calls it on the member at +0x18. A constructor gives 9 bytes, because it returns `this`. `void UnkTargetText::FUN_00137AF0() { unk0 = DAT_0035DC1C; }` in `src/game/auto/00137AF0.cpp` is `matched`. The donor has a wide-string holder with the same place and shape, so the member's type is `unsigned short*`, which is a guess. The match needs the shared header only for the name of the class.
- Revisit when: a function names what 0x0035DC1C holds.

## F-0103 Operator new at 0x000136D0 is game code and matches as ??2@YAPAXI@Z
- Status: confirmed
- Addresses: 0x000136D0, 0x00123060, 0x000136E0, 0x00053DD0
- Checked: ghidra-mcp disassemble_function on 0x000136D0 by the reviewer (2026-11-15); `uv run python -m bodecomp.match --check` and `uv run python -m bodecomp.names check` (2026-11-15); ghidra-mcp get_xrefs_to on 0x000136D0, and a compile of `src/game/auto/00053DD0.cpp` without the name, by the review of pull request #18 (2026-11-15); `uv run python -m bodecomp.sync check` by the lead and by the review of pull request #19 (2026-11-15)
- Evidence: 0x000136D0 is `MOV EAX,[ESP+4]`, `PUSH 4`, `PUSH EAX`, `CALL 0x00123060`, `ADD ESP,8`, `RET`, the mirror of operator delete at 0x000136E0 (F-0081). It has 610 references, from code across the whole of `.text`, and two of them are the jumps at 0x00011020 and 0x0021DE9E. `void* operator new(unsigned int size) { return FUN_00123060(size, 4); }` in `src/game/auto/000136D0.cpp` is `matched`, and `names set` recorded `??2@YAPAXI@Z` with the tier `matched`. Before the name, a global `new` in 0x00053DD0 named no entry in `config/symbols.txt`, so the matcher wrote a class `operator new` that called `FUN_000136D0`. The reviewer failed that form, because it exists only for the missing name. With the name, a global `new` gives 0x00053DD0 and 0x00053EE0 at 100%. Without the name, 0x00053DD0 gives 98.5%, because the call does not resolve, so the name has to be in the same pull request as the match. After the merge of pull request #18, the lead ran `sync apply` on main at 6a75910 (2026-11-15). It renamed 1 function in Ghidra, 0x000136D0 to `??2@YAPAXI@Z`, and `sync check` then gave 0 differences.
- Revisit when: a function calls operator new with another alignment than 4.

## F-0104 A member destructor declared throw() removes the unwind state write before its call
- Status: open
- Addresses: 0x000E3200, 0x0007CFB0, 0x000E3160, 0x0007CCD0, 0x000120E0, 0x0030FF50, 0x0030FF58
- Checked: the matcher's and the reviewer's compiles in the worktree of issue #9 (2026-11-15); ghidra-mcp disassemble_function on 0x000E3160, 0x0007CCD0, 0x000120E0, 0x000E3200 and 0x0007CFB0 by the reviewer (2026-11-15); the matcher's compiles in the batch of issue #32 (2026-11-17)
- Evidence: The destructors 0x000E3200 and 0x0007CFB0 destroy an array member with 0x000E3160 and 0x0007CCD0, which have the same bytes. With the member destructor declared only, VC71 writes the unwind state 0 before the call (`MOV byte ptr [ESP+0x10],0`), and 0x000E3200 gives 55.4%. The original has no such write. With `~Array_000E3280() throw();` both match, and the sources have that form. 0x000E3160 frees a vector of pointers through a pool, with the lock 0x000120E0 and a free list at 0x0030FF58, and the reviewer matched it at 100% from that body. With the body in the same source, 0x000E3200 matches only when `operator delete(void*) throw()` and `FUN_000120E0(int*) throw()` are declared too. `<new>` of VC71 declares operator delete with `throw()`, and no evidence gives `throw()` to 0x000120E0. 0x000B7340 and 0x00139550 match without `throw()`. The batch of issue #32 (2026-11-17) matched 0x000E3160 and 0x0007CCD0 at 100% from that body, with the address of the free list computed before the call of 0x000120E0. With the `throw()` gone from the member destructors, 0x000E3200 again needed `throw()` on both `operator delete` and `FUN_000120E0`, and gave 55.4% with only one of them. The reviewer failed the `throw()` on `FUN_000120E0` as code that steers the compiler, because no evidence supports it. With a definition of 0x000120E0 in the same source and no `throw()`, 0x000E3200 matched, but that definition gave only 7.9% to 12.9% against 0x000120E0. `bodecomp.match` reads only `declared` lines from headers, so an inline 0x000120E0 in a shared header would be compared as compiler-generated code. The batch kept the old form.
- Next: match 0x000120E0, then define it where every source that destroys the array can see it, and define 0x000E3160 and 0x0007CCD0 with their real bodies in place of the `throw()` on the member destructor.

## F-0105 The member of 0x000929C0 is a struct that holds the class of 0x00127860, and 0x00018810 is its destructor
- Status: confirmed
- Addresses: 0x000929C0, 0x00127860, 0x00018810, 0x00236430, 0x00236438, 0x002FCCC8, 0x002ECA00, 0x000B7340, 0x00127DA0, 0x0035D420, 0x0035D424
- Checked: ghidra-mcp read_memory on 0x002FCCC8, 0x00236430 and 0x00236438, disassemble_function on 0x000929C0 and 0x000B7340, and get_xrefs_to on 0x00018810 by the reviewer (2026-11-15); `uv run python -m bodecomp.match --check` (2026-11-15); compiles of the direct member and of a `// generated: 0x00018810` line by the review of pull request #18 (2026-11-15)
- Evidence: 0x00127860 is the virtual destructor of the class with the vtable 0x002ECA00. The function info 0x002FCCC8 of 0x000929C0 has 2 states, and the funclet 0x00236438 of state 1 jumps to 0x00018810, which is `JMP 0x00127860`, while the body calls 0x00127860 directly. The 12 references to 0x00018810 are all from funclets. The matcher wrote a forwarding destructor that called a member named `FUN_00127860`, and the reviewer failed it as steering code. A member of the class with the virtual destructor declared at 0x00127860 gives 95.2%, because the funclet then calls 0x00127860. A struct that holds that class as its only member gives 100%: VC71 emits the struct's destructor as the jump. Its destructor can be implicit or `{}`. With `// generated: 0x00018810` in `src/game/auto/000929C0.cpp`, the jump is `matched` from that source too. The batch of issue #32 (2026-11-17) removed the placeholder from `src/game/trivial/0001.cpp`. The jump is then `matched` only when 0x00127860 has a claim of its own, so `src/game/auto/00127860.cpp` defines the class with the six other slots of the vtable 0x002ECA00 and claims 0x00127860 and its deleting destructor 0x00127DA0, which calls 0x00123040 (F-0106). The destructor clears the globals 0x0035D420 and 0x0035D424 when they hold the object. The reviewer read the vtable through ghidra-mcp read_memory and the two destructors through get_functions.
- Revisit when: another class shows a member destructor that is only a jump.

## F-0106 A deleting destructor that calls 0x00123040 directly needs an operator delete that calls it
- Status: confirmed
- Addresses: 0x00123040, 0x000136E0, 0x0007CF90, 0x000B74D0, 0x000929A0, 0x00026320, 0x00096200, 0x00047ED0, 0x00053EE0
- Checked: ghidra-mcp disassembly of the deleting destructors by the matcher (2026-11-15); the reviewer's compiles (2026-11-15)
- Evidence: The deleting destructors 0x0007CF90, 0x000B74D0, 0x000929A0, 0x00026320 and 0x00096200 call 0x00123040, while 0x00047ED0 and 0x00053EE0 call operator delete 0x000136E0, which is `JMP 0x00123040` (F-0081). Without a class `operator delete` that calls `FUN_00123040`, six rows give 94.5% to 97.1%. A global inline `operator delete` in the source that calls `FUN_00123040` also gives 100% for 0x00026140 and 0x00026190. No evidence decides between the two forms. The sources have the class form.
- Revisit when: a string or the donor shows how the game declares its pool delete.

## F-0107 0x000BD710 is parked as scheduling at 83.7%
- Status: open
- Addresses: 0x000BD710, 0x000BA840, 0x000BA740, 0x00321760, 0x000B86F0, 0x000BB6C0
- Checked: the matcher's and the reviewer's compiles in the worktree of issue #9 (2026-11-15); `uv run python -m bodecomp.match` (2026-11-15); the matcher's compiles, ghidra-mcp search_instructions and get_xrefs_to, and the reviewer's search of the GC repo in the batch of issue #32 (2026-11-17)
- Evidence: The constructor is 442 bytes in both. About 12 forms of the matcher and 5 of the reviewer did not match. The best one, the reviewer's, loads the three constants into locals first and gives the stores in the original's order. The remaining difference: the original clears xmm0 before it loads the constant at 0x002E33F8 into xmm1, and the build loads in another order. Literal `0.0f` gives 48.7%, and `EVec2` and `EVec3` members with temporaries give 40.8%. 0x000BA840 holds the same statements as the second half of the body, and as an inline helper it makes the sizes equal but not the order. The batch of issue #32 (2026-11-17) tried about 40 more forms, and the 83.7% form stays. Locals for the constants in every order give 46.7% to 65.8%. Members whose own constructors store the constants give 37.8% to 46.1%, and an inline helper with the first-half stores gives 45.6%. The donor classes with a virtual `Unk802A2AC0` base, `Unk80026864` and `Unk8003AA6C`, have other members, and no donor source has the panel's arguments; the reviewer checked this. ghidra-mcp search_instructions for stores to +0x164, +0x16C and +0x188, and get_xrefs_to on the three constants, find no function that holds the first-half stores: 0x000B86F0 only clears +0x184 to +0x18C, and 0x000BB6C0 stores 0x178 to 0x180 without the other stores.
- Next: find another reading of the first half, for example stores that a constructor of the panel or of a base makes.

## F-0108 The unit of 0x00017D10 holds 3 bytes of code at 0x00017D70 that no function starts
- Status: open
- Addresses: 0x00017D10, 0x00017D70, 0x00017D80
- Checked: ghidra-mcp read_memory, find_functions and get_xrefs_to on 0x00017D70 by the matcher and the reviewer (2026-11-15)
- Evidence: The destructor 0x00017D10 ends with the `RET` at 0x00017D6F. The bytes at 0x00017D70 are `8B C1 C3` (`MOV EAX,ECX`, `RET`), then `CC`. Ghidra has no function there and no reference to it, and the next function starts at 0x00017D80. So the unit is 99 bytes, and the destructor's own 96 bytes are equal, 97.0%. The function is parked as `unclassified`, as the two units of F-0078 are.
- Next: create a function at 0x00017D70 with `tools/create-functions.sh`, cut the units again, and match the destructor.

## F-0109 Ghidra has no reference to 0x00321760 from 0x000BA883 or from 0x000BD710
- Status: open
- Addresses: 0x00321760, 0x000BA840, 0x000BA883, 0x000BD710
- Checked: ghidra-mcp get_xrefs_to on 0x00321760, get_xrefs_from on 0x000BA884 and disassemble_bytes on 0x000BA87C by the lead (2026-11-15); `build/target/relocs.tsv` by the matcher (2026-11-15); ghidra-mcp get_xrefs_to on 0x00321760, `_site` in `bodecomp/match.py` and `uv run pytest -q` by the review of pull request #18 (2026-11-15)
- Evidence: 0x000BA883 is `ADD EAX,0x321760` after `SHL EAX,5`, the address of an element of an array of 0x20-byte items. Ghidra has 5 references to 0x00321760, from 0x000BB6C0, 0x00241200 and 0x00243130, and none from 0x000BA840. The matcher reports the same `ADD` in 0x000BD710 with no relocation in its unit. The source of 0x000BD710 writes `&DAT_00321760[player]`, and the matcher reports that the built relocation compares equal there. That is the rule of `_site` in `bodecomp/match.py`: at a site where the unit has no relocation, the four bytes of the original are the expected address (`DIR32`) or the expected call target (`REL32`), and the built relocation must resolve to it. `test_call_the_delinker_dropped_compares_with_the_literal_offset` tests the `REL32` case, and `test_address_the_delinker_dropped_compares_with_the_literal_address` tests the `DIR32` case. So a missing reference in Ghidra does not hide a difference from the check.
- Next: add the references at the namer step.

## F-0110 The callers batch shows no gain from the shared bases, so the trial's outcome is no gain
- Status: confirmed
- Addresses: 0x00137AF0, 0x000136D0, 0x00053DD0, 0x000BD710
- Checked: the token counts and the matched bytes in `docs/thunk-trial-results.md`, "Batches" (2026-11-15); `comm` of the `matched` rows of `config/functions.csv` at 025508c and at 6a75910, with the sizes in `config/symbols.txt` (2026-11-15); the byte shape of the units of the 57 functions, read with `bodecomp.trivial.masked`, by the review of pull request #19 (2026-11-15)
- Evidence: The callers batch cost 32,848 tokens per matched function, 4.3 times the 7,557 of M4 batch 3, and the figure leaves out the lead's tokens. The trial matched 57 functions that were not matched before it. 13 of them have 16 bytes or fewer: 11 thunks, operator new 0x000136D0 and 0x00137AF0. So 0x00137AF0 is the only function of the 47 of F-0080 that the trial matched, and it stores a data address, not a vtable (F-0102). The maintainer ruled on 2026-11-15 that it does not count. Per matched byte, the callers batch cost 340 tokens and batch 3 cost 445. No batch of larger functions without the shared bases has a measured cost, so the lower figure can come from the larger functions alone, which is a guess. The figure also leaves out the lead's tokens. If the lead's part was more than about 181,000 tokens, the callers batch costs more per byte than batch 3 too. By the spec's Outcomes table, the outcome is "no gain".
- Revisit when: a matcher batch of functions of about 100 bytes without the shared bases has a measured cost, or a rule says how the tokens of a lead session are measured.

## F-0111 0x001C2890 is parked as source shape at 73.7%
- Status: open
- Addresses: 0x001C2890
- Checked: the matcher's compiles in the worktree of night batch 1 (2026-11-24); ghidra-mcp disassemble_function by the lead (2026-11-24)
- Evidence: The function is `MOV AX,[ECX]`, `CMP AX,0xffff`, `JNZ`, `OR AX,AX`, `RET`, then `AND AH,0x7f`, `RET`. The matcher reports that each of about 10 forms gives `and eax,0x7fff` or `and ax,0x7fff`: `unsigned short` and `short` locals, `r &= 0x7FFF`, a shift pair and casts. The reviewer did not check the count of forms. The kept form returns `v` when it is 0xFFFF and `v & 0x7FFF` otherwise. The function has an `auto` name and no known class, so no donor form was compiled.
- Next: try a 15-bit bit-field with a 1-bit flag above it, and a byte-wise form that clears bit 7 of the high byte.

## F-0112 0x001EF8E0 and 0x0020FD40 match when the null test is an inline member of the pointed-to class
- Status: confirmed
- Addresses: 0x001EF8E0, 0x0020FD40
- Checked: `uv run python -m bodecomp.match`, run again by the reviewer in the worktree of night batch 1 (2026-11-24); the reviewer's compiles of three other forms of 0x0020FD40 in a copy of the worktree of night batch 2, and ghidra-mcp disassemble_function (2026-11-24)
- Evidence: The form with an inline `Inner::get()` (`if (data) return data[-2]; return 0;`) called as `in->get()` matches at 100% in src/game/auto/001E.cpp. The matcher reports 76.5% for the form that reads `in->data` in the outer member, where the build loads `in` into EAX and the original keeps ECX, and 88.2% for a ternary inside `get()`. The reviewer of night batch 1 did not compile those two forms (F-0077). 0x0020FD40 is `mov ecx,[ecx+8]; mov eax,[ecx]; test eax,eax; jz; mov ax,[eax-4]; ret; xor eax,eax; ret`. The reviewer of night batch 2 compiled three forms that read `inner->p` in the outer member: an `if` gives 66.7%, a local gives 66.7% and a ternary gives 76.5%, each with the first difference at +0x1. An inline `Inner::size()` called as `inner->size()` gives 100%.
- Revisit when: a function of this shape matches only with the test in the outer member.

## F-0113 Four setters write a member of a virtual base at the vbptr offset plus the member offset
- Status: open
- Addresses: 0x001A6C10, 0x001B5210, 0x001D9610, 0x001F8AA0
- Checked: `uv run python -m bodecomp.match`, run again by the reviewer in the worktree of night batch 1 (2026-11-24)
- Evidence: The bytes are `mov eax,[ecx+0x20]; mov edx,[eax+4]; mov eax,[esp+4]; mov [edx+ecx+K],eax; ret 4`, with K = 0x24, 0x30, 0x28 and 0x34. A class with a 0x20-byte non-virtual base and one virtual base matches all four at 100%, with the member at K - 0x20 in the virtual base: 4, 0x10, 8 and 0x14. The matcher reports 94.1% for the form with K as the member offset. The reviewer did not compile that form (F-0077).
- Next: compile the form with K as the member offset and compare the bytes, then set the entry to confirmed.

## F-0114 The string length loop of 0x001A4FD0 matches with an end pointer taken before the loop
- Status: open
- Addresses: 0x001A4FD0
- Checked: `uv run python -m bodecomp.match`, run again by the reviewer in the worktree of night batch 1 (2026-11-24)
- Evidence: `const char* p = s; const char* e = p + 1; char c; do c = *p++; while (c); return p - e;` matches at 100% in src/game/auto/001A.cpp. The matcher reports 5.3% for `while (*p++);` with `return p - s - 1`. The reviewer did not compile that form (F-0077).
- Next: compile the `while (*p++)` form and compare the bytes, then set the entry to confirmed.

## F-0115 0x0021B4A0 is parked as source shape at 64.7%
- Status: open
- Addresses: 0x0021B4A0
- Checked: ghidra-mcp disassemble_function by the reviewer (2026-11-24); the matcher's compiles in the worktree of night batch 2 (2026-11-24)
- Evidence: The function is `mov al,[ecx]; mov ecx,[esp+4]; and al,[ecx]; neg al; sbb eax,eax; neg eax; ret 4`. It loads `*this` before the argument. The matcher reports that 9 forms load the argument first: the operands in both orders, `const char*` and `const S*` arguments, `char`, `unsigned char` and `bool` members, locals, a static helper, and `? :` and `if` returns. 7 give 64.7% and 2 give 0%. The reviewer did not compile them. The kept form is `(m & o->m) != 0`.
- Next: try an inline helper of the class of the argument, as in F-0094 and F-0112, and read the callers in Ghidra to learn what the byte is.

## F-0116 0x00063CB0 matches with an if-return, not with a logical or
- Status: confirmed
- Addresses: 0x00063CB0
- Checked: the matcher's compiles in the worktree of night batch 3 and the reviewer's compile in a copy of it, with ghidra-mcp disassemble_function (2026-11-24)
- Evidence: The function is `cmp [ecx+0x52c],0; mov al,1; jg; mov al,[ecx+0x564]; ret`. `return n > 0 || b;` gives 29.6%, with the first difference at +0x7; the reviewer compiled it again. `if (n > 0) return true; return b;` gives 100% in src/game/auto/0006.cpp.
- Revisit when: a function of this shape matches only with `||`.

## F-0117 0x000D9960 is parked as scheduling at 61.1%
- Status: open
- Addresses: 0x000D9960, 0x000D66A0, 0x000D66C0, 0x000D9AC0, 0x000D9AE0, 0x000DFAA0
- Checked: the matcher's compiles in the worktree of night batch 3, ghidra-mcp search_instructions and disassemble_function by the matcher and the reviewer (2026-11-24); the matcher's and the reviewer's compiles of night batch 12 (2026-11-24); the matcher's compiles in the worktree of night batch 15 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The function is `or byte [ecx+0x5b],0x10; mov [ecx+0x50],eax; or dword [ecx+8],2; ret 4`. VC71 puts `or [ecx+8],2` before the byte `or`. The matcher reports 10 forms: 9 give 61.1% (each statement order but one, a `char` flag byte, bit-fields, inline helpers with the +8 flag set last, a base-class helper, an out-of-line setter), and the order with the +8 flag first gives 44.4%. The reviewer did not compile them. A search for `or byte [reg+0x5b],0x10` finds setters with the same order: 0x000D66C0 (a float store), 0x000D9AC0 and 0x000D9AE0 (on an inner object) and 0x000DFAA0 (after a null test). 0x000D66A0 has the byte `or` and no `or [+8],2`. None of them is a shared helper. Night batch 12 parked 0x000D9AC0 and 0x000D9AE0 as scheduling at 71.4% for the same reason: every form VC71 builds puts `or dword [eax+8],2` before the store to +0x50, or reloads `[ecx+0x5c]`. The matcher tried five forms (statement order, a local pointer, `t->` three times, a byte member against bit-fields, inline setters), and the reviewer compiled five forms in a scratch copy with the same result. Neither function has an xref in Ghidra (get_xrefs_to, 2026-11-24). Night batch 15 matched 0x000D66A0 with a plain statement order, since it has no `or [+8],2`. It parked 0x000D66C0 at 59.1% and 0x000DFAA0 at 68.2% as scheduling. In both, `fl |= 0x10; f = v; flags |= 2;` builds `or dword [ecx+8],2` before the store, and putting the store first gives the same code. A local reference `unsigned& r = flags;` declared first, or a pointer `unsigned* r = &flags;`, gives the original order and 100%, which the reviewer compiled. The reviewer failed that form under S1, because the reference exists only to reorder the code (ADR-0013), so the lead set both back to the plain form.
- Next: find a form that keeps the order and is not a steering trick, for example a setter of a base class that the original also calls, then match the group.

## F-0118 0x0010A4D0 is parked as source shape at 94.4%, because only a volatile parameter matches
- Status: open
- Addresses: 0x0010A4D0
- Checked: the matcher's compiles in the worktree of night batch 4, the reviewer's compile of the `unsigned` form in a copy, ghidra-mcp disassemble_function and get_xrefs_to by the reviewer (2026-11-24)
- Evidence: The function is `mov eax,[ecx]; mov edx,[esp+4]; and eax,0xffff8000; or eax,edx; mov [ecx],eax; ret 4`. `v = (v & 0xFFFF8000) | x;` with `unsigned x` gives 11.1%, because VC71 folds the argument into `or eax,[esp+4]` (16 bytes against 18); the reviewer compiled it again. `const unsigned&` gives 94.4% and is the kept form. `volatile unsigned x` gives 100%, but the reviewer failed it under S1, because a volatile on a parameter passed by value has no other use than to steer the compiler. The matcher reports that `int`, `unsigned short`, a struct with one member passed by value, a 15 and 17 bit-field pair and a volatile member do not match. Ghidra has no reference to the function.
- Next: find the type of the argument through a caller or a vtable of the class.

## F-0119 Constructors that clear 11 to 21 dwords match with memset, and one that clears 256 dwords with a loop
- Status: confirmed
- Addresses: 0x001430C0, 0x001893F0, 0x001B0010, 0x0019A3D0
- Checked: the matcher's compiles in the worktree of night batch 4, and the reviewer's compile of the loop form of 0x001B0010 in a copy (2026-11-24)
- Evidence: `memset(this, 0, sizeof(*this))` gives `xor eax,eax; mov ecx,N; mov edi,edx; rep stosd; mov eax,edx` and matches 0x001430C0 (21 dwords), 0x001893F0 (15) and 0x001B0010 (11). A `for` loop that clears the members is unrolled at these sizes: the reviewer got 2.6% for 0x001B0010 (39 bytes against 32), and the matcher reports 1.4% to 2.6% for the other two. 0x0019A3D0 (256 dwords) matches with the `for` loop; `memset` was not tried there.
- Revisit when: a constructor that clears between 22 and 255 dwords is matched.

## F-0120 0x001DADA0, 0x001E42B0, 0x001E42E0 and 0x001E4310 read members at negative offsets from this and are parked as source shape
- Status: open
- Addresses: 0x001DADA0, 0x001E42B0, 0x001E42E0, 0x001E4310, 0x001E4230, 0x001E42A0, 0x001E42D0, 0x001E4300, 0x002F3D28, 0x002F3D44, 0x002F3D48, 0x002F3D4C, 0x001A9520, 0x001AE3E0, 0x001B5E00, 0x001E3830, 0x001B66A0, 0x001B6690, 0x001DACD0, 0x001E3FF0, 0x001AE550, 0x001AE540, 0x001B5F00, 0x001E3930, 0x001DA8A0, 0x001E3F70, 0x001AE130, 0x001AEAF0, 0x001AEB40, 0x001AEE40, 0x001AE120, 0x001AEAE0, 0x001AEB30, 0x001AEE30, 0x001B5C20, 0x001E3640, 0x001B6150, 0x001E3B80, 0x001B6170, 0x001E3BA0, 0x001B6350, 0x001E3D80, 0x001DAD40, 0x001FA200, 0x001AF340, 0x001AF330, 0x001B7450, 0x001E4590, 0x001A72B0, 0x001B52F0, 0x001D9700
- Checked: ghidra-mcp disassemble_function and get_xrefs_to by the reviewer of night batch 4 (2026-11-24); ghidra-mcp disassemble_function, get_xrefs_to and read_memory at 0x002F3D20 by the reviewer of night batch 5 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to by the reviewer of night batch 13 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to by the reviewer of night batch 14 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to by the matcher and the reviewer of night batch 16 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to and a scratch compile by the reviewer of night batch 17 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to by the matcher and the reviewer of night batch 26 (2026-11-24); ghidra-mcp disassemble_function and get_xrefs_to by the reviewer of night run batch 4 of the run of 2026-11-24, with scratch compiles of a virtual-base class and a secondary-base override
- Evidence: 0x001DADA0 is `xorps xmm0,xmm0; comiss xmm0,[ecx-0x51C]; jbe; mov al,1; ret`, and 0x001E42B0 is `mov al,[ecx-0x560]; and al,1; sub al,1; neg al; sbb eax,eax; add eax,1; ret`. The only reference to each is a jump from a `SUB ECX,[ECX-4]; JMP` thunk, 0x001E4230 and 0x001E42A0, and the thunks are referenced as data from 0x002F3D28 and 0x002F3D44. F-0087 gives this thunk shape for a class with a virtual base, where the override receives `this` as a pointer to the virtual base. The matcher's sources read the members through a cast such as `(char*)this - 0x51C` and give 100%. The reviewer failed both under S1, because the cast stands in for the class layout that VC71 generates (ADR-0013). That the negative offsets are members of the derived class seen from the virtual base is a guess from the thunk bytes and F-0087; nobody compiled a class with a virtual base for these two. Night batch 5 found two more: 0x001E42E0 reads `[ecx-0x554]` as `(x & 1) == 1`, and 0x001E4310 reads it as `(x & 2) == 2`. Each is called only from a thunk of the same shape, 0x001E42D0 and 0x001E4300, and those thunks are referenced as data from 0x002F3D48 and 0x002F3D4C, in the same table as the first two thunks. The matcher reports 11% for one class with a virtual base and an override, which read the member at a positive offset; the reviewer did not compile it. Night batch 13 found one more: 0x001A9520 reads `[ecx-0x34]` and `[ecx-0x30]`, writes them through its two pointer arguments and ends with `ret 8`. Its only references are the jumps of three thunks, 0x001AE3E0, 0x001B5E00 and 0x001E3830, each `SUB ECX,[ECX-4]` and `JMP 0x001A9520`, two of them with `ADD ECX,0x1D0` or `0x1C4` between. The matcher's cast `(char*)this - 0x34` gives 100%; the reviewer failed it under S1 and the lead parked it as source shape. Night batch 14 found two more. 0x001B66A0 reads `[ecx-0x84]` and `[ecx-0x80]` and ends with `ret 4`; its only reference is the jump at 0x001B6693 in the thunk 0x001B6690. 0x001DACD0 reads `[ecx-0x5EC]` and `[edx+ecx-0x508]`; its only reference is the jump at 0x001E3FF3 in the thunk 0x001E3FF0. Both thunks are `SUB ECX,[ECX-4]; JMP`. The matcher's cast from `this` gave 100% for 0x001B66A0; the reviewer failed it under S1 and the lead parked it as source shape. 0x001DACD0 was already parked (F-0139). Night batch 16 parked 0x001AE550 as source shape at 13.6%: it is `mov eax,[ecx-0x14C]; mov cx,[esp+8]; mov edx,[esp+4]; mov [eax+edx*2],cx; ret 8`, and its only references are the jumps of three thunks, 0x001AE540, 0x001B5F00 and 0x001E3930, each `SUB ECX,[ECX-4]` and `JMP 0x001AE550`, two of them with `ADD ECX,0x1D0` or `0x1C4` between. The kept source reads at +0, and no other form was compiled. Night batch 17 found one more: 0x001DA8A0 is `mov eax,[esp+4]; movss xmm0,[esp+8]; movss [ecx+eax*4-0x548],xmm0; ret 8`, and its only reference is the jump at 0x001E3F73 in the thunk 0x001E3F70 (`SUB ECX,[ECX-4]; JMP`). The matcher's `float a[0x200]; a[n - 0x152] = v;` gives 100% without a cast, and the reviewer's cast form `((float*)this)[n - 0x152]` also does. The reviewer failed the negative index under S1, because it stands in for the virtual-base layout in the same way as the cast, and the lead parked it as source shape. Night batch 26 parked four more as source shape. 0x001AE130 reads `[ecx-0x70]`, 0x001AEAF0 and 0x001AEB40 copy the dwords at `[ecx-0x8c]` and `[ecx-0x88]`, and 0x001AEE40 returns bit 9 of the word at `[ecx-0x11e]`. Each has three references, the jumps at +3 of three `SUB ECX,[ECX-4]; JMP` thunks (0x001AE120, 0x001B5C20, 0x001E3640; 0x001AEAE0, 0x001B6150, 0x001E3B80; 0x001AEB30, 0x001B6170, 0x001E3BA0; 0x001AEE30, 0x001B6350, 0x001E3D80). The cast sources give 100% for 0x001AEAF0 and 0x001AEB40; the units of 0x001AE130 and 0x001AEE40 also hold a thunk (F-0154). 0x001DAD40 (`mov ecx,[esi-0x160]; call [eax+0x1c]; mov word [esi-0x540],0`, called only from 0x001E38C0) and 0x001FA200 (`mov eax,[ecx-0x6c]; mov edx,[eax+8]; ...; call [eax+0x1ac]; movsx eax,word [eax+0x5c]`, called only from 0x001FA1F0) have the same shape. Their sources matched at 100% only with `char*` casts and, for 0x001FA200, a hand-written vbtable read, so the reviewer failed them under S1 and they are parked as source shape. A scratch class with virtual bases gives the same vbtable chain with other displacements, and a secondary-base override gives `add ecx,-0x68; jmp [eax]`. Night batch 2 of 2026-11-25 parked two more as source shape. 0x001AF340 is `mov edx,[ecx-0x60]; sub edx,[ecx-0x64]; mov eax,0x38e38e39; imul edx; sar edx,3; ...; ret`, a signed count of 36-byte elements minus 1, and its only references are three `SUB ECX,[ECX-4]; JMP` thunks, 0x001AF330, 0x001B7450 and 0x001E4590. Its source matched at 100% only through `(char*)this - 0x64`. 0x001A72B0 reads `[this+4]`, then `[vbtable+8]`, and calls slot 0x260 of the virtual base with the short at +0x5A. Its source matched at 100% with a hand-written vbtable read. The reviewer compiled `struct A : virtual T0, virtual T` with a member that calls the slot, and VC71 built the same instruction stream, with a different offset for the short only because the pad was 4 bytes too long (scratch compile, 2026-11-25). The reviewer failed both under S1 (ADR-0013). Night batch 3 of 2026-11-25 parked 0x001B52F0 and 0x001D9700 as source shape at 29.6%. Each reads `[ecx+4]`, then `[vbtable+8]`, `lea eax,[edx+ecx+4]`, then the vbptr at +0x20 of that base and `[vbtable2+4]`, and stores the stack argument at +0x30 (0x001B52F0) or +0x28 (0x001D9700), then `ret 4`. Ghidra has no reference to either (disassemble_function and get_xrefs_to, 2026-11-25). Like 0x001A72B0 they read through `this` with no `SUB ECX,[ECX-4]` thunk. The kept source, a class with two levels of virtual bases, builds a one-hop chain, and an explicit upcast form gives 6.0%.
- Next: read the vtables at 0x002F3D28 and 0x002F3D44, write the class with its virtual base, and match the two functions as overrides.

## F-0121 0x001E8280 takes its argument in EAX and is parked as unclassified
- Status: open
- Addresses: 0x001E8280, 0x001E8270, 0x0019B2A0, 0x001948F0, 0x001A4FA0, 0x001BC7F0
- Checked: ghidra-mcp disassemble_function, get_xrefs_to and read_memory at 0x001E8260 by the reviewer and the lead (2026-11-24); ghidra-mcp disassemble_function, get_xrefs_to and read_memory and the reviewer's compiles in a scratch copy for 0x0019B2A0 in night batch 21 (2026-11-24)
- Evidence: The function is `test eax,eax; jg; cmp eax,-3; jl; mov eax,1; ret; xor eax,eax; ret`, which is `x <= 0 && x >= -3` with `x` in EAX. Nothing in it sets EAX before the first test. Ghidra has no reference to it. 0x001E8270 is a complete function (`mov eax,[esp+4]; mov [0x003DD8B8],eax; ret`), followed by `cc` padding up to 0x001E8280, so 0x001E8280 is not its tail and not a shared return (F-0078). No VC71 calling convention that a source can name passes the first argument in EAX, so `bool f(int x)` gives 0%. The matcher parked it as `register tie` after one form; the reviewer rejected that class, because an instruction is missing, not only a register name, and the lead set it to `unclassified`. Night batch 21 parked 0x0019B2A0 as unclassified at 95.7% for the same reason. Night batch 1 of 2026-11-25 parked 0x001948F0 as unclassified at 0% for the same reason: `cmp word [eax],0; jz; mov dl,[eax]; mov [ecx],dl; add eax,2; add ecx,1; ...; mov [ecx],0; ret` copies a string of shorts from EAX to chars at ECX, and Ghidra has no reference to it (disassemble_function and get_xrefs_to by the reviewer, 2026-11-25). The matcher tried one `__fastcall` form and had no donor. Night batch 2 of 2026-11-25 parked 0x001A4FA0 and 0x001BC7F0 as unclassified at 0% for the same reason: each copies a string of shorts from EAX to chars at ECX, and Ghidra has no reference to either (reviewer, 2026-11-25). It is a linked-list search, `mov eax,[eax]; test; jz; cmp [eax],ecx; jz; mov eax,[eax+8]; test; jnz; xor al,al; ret; mov al,1; ret`, with the head in EAX and the key in ECX. `bool __fastcall f(int key, S**)` builds the same code with EDX for EAX, the only difference at +0x1; cdecl gives 9.1% and `__stdcall` 8.1%. Ghidra has no reference to it, and `cc` padding follows the `ret 4` before it.
- Next: find a caller that sets EAX, for example through an indirect call, or learn whether the original was built with a whole-program option that changes calling conventions.

## F-0122 0x0020F4E0 matches when the member pointer is copied to a local before the null test
- Status: confirmed
- Addresses: 0x0020F4E0
- Checked: the matcher's compiles in the worktree of night batch 5, the reviewer's compile in a copy, and ghidra-mcp disassemble_function (2026-11-24)
- Evidence: The function is `mov ecx,[ecx+8]; test; jz; mov eax,[ecx]; push -1; call [eax+8]`. A local copy of the member before the test gives 100%. The reviewer compiled `if (p) return p->FUN_Slot2(-1);` on the member and got 5.0%, with the first difference at +0x0.
- Revisit when: a function of this shape matches only with the test on the member.

## F-0123 0x0010BBE0 ends in dec on a member, where the default flags give add -1, and is parked as unclassified
- Status: open
- Addresses: 0x0010BBE0, 0x0010BD6D, 0x0010BFA6, 0x0010C55E, 0x0004A920
- Checked: ghidra-mcp disassemble_function and search_instructions by the reviewer (2026-11-24); the matcher's compiles in the worktree of night batch 6 (2026-11-24)
- Evidence: The function is `mov eax,[esp+4]; mov dword [eax],0; dec dword [ecx+0x4500]; ret 4`, with the `dec` bytes `ff 89 00 45 00 00`. The matcher reports that VC71 at the default flags gives `add dword [ecx+0x4500],-1` for `--n`, `n--`, `n -= 1`, `n = n - 1`, an unsigned member, an inline `Dec()` of a member struct and `(*p)--`, each at 70% with the first difference at +0xA. The reviewer did not compile them. Ghidra has the same `dec` on a member at 0x0010BD6D and 0x0010BFA6 (`[reg+0x10C]`) and at 0x0010C55E (`[ebx+0x4500]`, the same member). At the default flags 0x0004A920 matches with `add [mem],1` (F-0022). That this region was built with other flags is a guess; nobody compiled it at other flags.
- Next: compile 0x0010BBE0 in a scratch directory at `/G6`, `/Os` and `/Ox`, compare the bytes, and record the result next to F-0018. Night batch 10 found the same kind of difference in 0x0010B770: the original ends in `inc eax` and the build gives `add eax,1` (F-0128).

## F-0124 The unit of 0x001637E0 holds a second function at 0x001637F0 that Ghidra has not created
- Status: fixed (3e23c03)
- Addresses: 0x001637E0, 0x001637F0, 0x00124255, 0x001F50F7
- Checked: ghidra-mcp get_xrefs_to, find_functions and disassemble_function by the reviewer (2026-11-24); `uv run python -m bodecomp.match` in the worktree of night batch 7 (2026-11-24); `tools/create-functions.sh`, `sync export`, `split`, `delink.sh`, `relink` and `uv run python -m bodecomp.match` on the branch of issue #94 (2026-11-24)
- Evidence: The unit runs from 0x001637E0 to 0x00163800: `c2 04 00`, 13 `cc` bytes, then `c2 04 00`. Ghidra has the function 0x001637E0, a single `RET 0x4` that 0x001F50F7 calls. It has no function at 0x001637F0, which `JMP 0x001637f0` at 0x00124255 in 0x00124240 reaches after `MOV [ESP+4],EAX`. So 0x001637F0 is a real entry and not a shared return. The source of 0x001637E0 builds 3 of the 19 bytes, 15.8%, and the function is parked as `unclassified`, as the units of F-0078 and F-0108 are. Issue #94 created the function 0x001637F0. After the rebuild the analysis had put it into the body of 0x00124240 as a second chunk, so only `starts` mode with the full list made it a function of its own, and 0x00124240 shrank from 32 to 29 bytes. After the new units, 0x001637E0 matches at 100%.
- Revisit when: a later rebuild puts 0x001637F0 back into the body of 0x00124240.

## F-0125 Two forms of night batch 7 match only in one statement order
- Status: confirmed
- Addresses: 0x0016ACF0, 0x0018E450
- Checked: the matcher's compiles in the worktree of night batch 7 and the reviewer's compiles in a copy (2026-11-24)
- Evidence: 0x0016ACF0 matches with `if (i <= n) return p; return 0;`, and `if (i > n) return 0; return p;` gives 73.7% with the first difference at +0x7. 0x0018E450 matches with `y += o.y; x += o.x;`, and the order with `x` first gives 52.6% with the first difference at +0x7. The reviewer compiled both other forms.
- Revisit when: a function of these shapes matches only in the other order.

## F-0126 The unit of 0x001C0A20 holds a second function at 0x001C0A30 that Ghidra has not created
- Status: fixed (3e23c03)
- Addresses: 0x001C0A20, 0x001C0A30, 0x002F2F08, 0x002F2F0C
- Checked: ghidra-mcp get_xrefs_to, disassemble_function and read_memory by the reviewer (2026-11-24); `uv run python -m bodecomp.match` in the worktree of night batch 8 (2026-11-24); `tools/create-functions.sh`, `sync export`, `split`, `delink.sh`, `relink` and `uv run python -m bodecomp.match` on the branch of issue #94 (2026-11-24)
- Evidence: 0x001C0A20 is 16 bytes and ends with `RET` at 0x001C0A2F. The unit goes on with `33 C0 C3` (`xor eax,eax; ret`) at 0x001C0A30, where Ghidra has no function. The vtable at 0x002F2F00 lists 0x001C0A20 at 0x002F2F08 and 0x001C0A30 at 0x002F2F0C, so 0x001C0A30 is a virtual function. The source of 0x001C0A20 gives 84.2%, the 3 bytes of 0x001C0A30 being the only difference, and the function is parked as `unclassified`, as F-0124 is. Issue #94 created the function 0x001C0A30. After the new units, 0x001C0A20 matches at 100%.
- Revisit when: a later rebuild drops the function 0x001C0A30.

## F-0127 A mask written as ~3 matches where 0xfc does not
- Status: confirmed
- Addresses: 0x001C2840, 0x001C2860
- Checked: the matcher's compiles in the worktree of night batch 8 and the reviewer's compiles in a copy (2026-11-24)
- Evidence: `((a + b + 3) & ~3) * 2 + 16` on `unsigned char` members matches both functions. With `& 0xfc` both give 0.0%, with the first difference at +0x0; the reviewer compiled that form. The matcher reports that `& 0xfc` gives `and eax,0xfc` and `& ~3` gives `movzx` and `and al,0xfc`; the reviewer did not read the instructions.
- Revisit when: a function of this shape matches only with `0xfc`.

## F-0128 The unit of 0x0010B770 holds a second function at 0x0010B780 that Ghidra has not created
- Status: open
- Addresses: 0x0010B770, 0x0010B780
- Checked: ghidra-mcp disassemble_function, read_memory and get_xrefs_to by the reviewer (2026-11-24); `uv run python -m bodecomp.match` in the worktree of night batch 10 (2026-11-24); `tools/create-functions.sh`, `sync export`, `split`, `delink.sh`, `relink` and `uv run python -m bodecomp.match` on the branch of issue #94 (2026-11-24)
- Evidence: 0x0010B770 is `mov eax,[ecx]; and eax,0x7fff; sub eax,3; neg eax; sbb eax,eax; inc eax; ret` and ends at 0x0010B77F. The unit goes on with `8b 41 4c c3` (`mov eax,[ecx+0x4c]; ret`) at 0x0010B780, where Ghidra has no function and no reference. The best source, `!((v & 0x7fff) - 3)` as `int`, gives 70%: it lacks those 4 bytes and has `add eax,1` for `inc eax`, the difference of F-0123. The matcher reports 35% for `== 3` as `bool` and 45% for an if-return. The function is parked as `unclassified`, as F-0124 and F-0126 are. Issue #94 created the function 0x0010B780, so the unit of 0x0010B770 is now 16 bytes. The kept form gives 77.8%: the only difference left is `add eax,1` in the build against `inc eax` in the original (first difference at +0xE, 18 bytes built against 16), as in F-0123. `(v & 0x7fff) == 3` as `int` and as `bool` give 38.9%. The function stays parked as `unclassified`.
- Next: settle F-0123 (a build at other flags), then match 0x0010B770 and the new 0x0010B780.

## F-0129 0x0018E580 calls a virtual function of a virtual base and is parked as unclassified at 4.8%
- Status: open
- Addresses: 0x0018E580
- Checked: ghidra-mcp disassemble_function, force_decompile and get_xrefs_to by the reviewer (2026-11-24); the matcher's compiles in the worktree of night batch 10 (2026-11-24)
- Evidence: The function is `test ecx,ecx; jz; mov eax,[ecx]; mov edx,[eax+0xc]; mov eax,[ecx+edx]; add ecx,edx; jmp [eax+0x2c]; xor eax,eax; ret`: when `this` is not null, it calls slot 11 of the third virtual base, found through the vbtable entry at +0xc. Ghidra has no reference to it. The matcher reports 4.8% for a class with three virtual bases and `this ? C::c11() : 0`, which VC71 compiles as a direct call, and 0% for a free function. An unqualified virtual call was not tried.
- Next: try `c11()` as an unqualified virtual call through the virtual base, and look for the vtable that holds 0x0018E580.

## F-0130 The unit of 0x00011B90 holds a second function at 0x00011BA0 that Ghidra has not created
- Status: open
- Addresses: 0x00011B90, 0x00011BA0
- Checked: ghidra-mcp disassemble_function, read_memory and get_xrefs_to by the matcher and the reviewer (2026-11-24); `uv run python -m bodecomp.match` in the worktree of night batch 11 (2026-11-24)
- Evidence: 0x00011B90 is 16 bytes, `8B C1 33 C9 89 08 89 48 04 89 48 08 89 48 0C C3`: it zeroes four ints and returns `this`, and Ghidra ends it at 0x00011B9F. The unit goes on with `8B C1 C2 04 00` (`mov eax,ecx; ret 4`) at 0x00011BA0, then `cc` padding to 0x00011BB0. `disassemble_function` finds no function at 0x00011BA0, and `get_xrefs_to` gives no reference to either address. The source builds 16 of the 21 bytes, 76.2%, and the function is parked as `unclassified`, as F-0124, F-0126 and F-0128 are.
- Next: find out whether 0x00011BA0 is a real entry (look for a vtable or table that holds it), create the function as issue #94 did, then match both.

## F-0131 A pointer converted to its third virtual base matches 0x001B6550
- Status: open
- Addresses: 0x001B6550
- Checked: the matcher's compiles in the worktree of night batch 11 (2026-11-24); ghidra-mcp disassemble_function by the reviewer (2026-11-24)
- Evidence: The original loads the pointer at `this-0x70`, tests it for null, then adds `[[p]+0xc]` to it. A `D*` converted to `V3*`, with `struct D : virtual V1, virtual V2, virtual V3`, matches at 100%. The matcher reports that a raw-pointer form does not match; the reviewer did not compile that form.
- Next: a reviewer compiles the raw-pointer form and compares the bytes (F-0077); set the entry to confirmed if it does not match.

## F-0132 A constant-size zeroing of a member array matches 0x001E75C0 only through memset
- Status: open
- Addresses: 0x001E75C0, 0x00033610, 0x0010E540, 0x0010E560
- Checked: the matcher's compiles in the worktree of night batch 11 (2026-11-24); ghidra-mcp disassemble_function and the reviewer's compiles in a scratch copy for 0x00033610 in night batch 18 (2026-11-24); ghidra-mcp disassemble_function and the reviewer's compiles in a scratch copy for 0x0010E540 in night batch 20 (2026-11-24)
- Evidence: `memset(v, 0, sizeof(v))` on the member array at `this->v[0x50]`, with `extern "C" void* __cdecl memset(void*, int, unsigned int);` declared in the source, matches at 100%. The matcher reports that plain loops build 18 bytes and that `#include <string.h>` fails with C1034, because the build has no include path. The reviewer did not compile the other forms. Night batch 18 found the same pattern at 0x00033610: `mov edx,ecx; push edi; mov ecx,0x10; xor eax,eax; lea edi,[edx+4]; mov [edx],0; rep stosd; pop edi; ret`. `n = 0; memset(items, 0, sizeof(items));` with `memset` declared in the source matches at 100%. The reviewer compiled the loop form `n = 0; for (i < 16) items[i] = 0;` (5.1%, 59 bytes built against 32) and the loop before `n = 0` (0.0%, 53 bytes). The loop forms of 0x001E75C0 itself are still compiled only by the matcher. Night batch 20 matched 0x0010E540 (`mov ecx,0x100`) and 0x0010E560 (`mov ecx,0x80`) the same way. For 0x0010E540 the reviewer compiled `for (i < 256) a[i] = 0; n = 0;` (13.0%, 19 bytes built against 23) and the loop after `n = 0` (8.7%, 21 bytes).
- Next: a reviewer compiles the plain-loop forms and compares the bytes (F-0077); set the entry to confirmed if they do not match.

## F-0133 A virtual forwarder matches 0x001AEF90 only when it returns the callee's value
- Status: open
- Addresses: 0x001AEF90
- Checked: the matcher's compiles in the worktree of night batch 11 (2026-11-24); ghidra-mcp disassemble_function by the reviewer (2026-11-24)
- Evidence: The original sign-extends the argument and tail-jumps through `jmp [eax+0x48]`. With slot 18 declared as `int FUN_s18(int)` and the method returning its result, the source matches at 100%. The matcher reports that with a `void` return VC71 puts the `movsx` before the `ecx` load; the reviewer did not compile that form.
- Next: a reviewer compiles the `void` return form and compares the bytes (F-0077); set the entry to confirmed if it does not match.

## F-0134 Two bit-field stores keep their order only inside an inline member function
- Status: confirmed
- Addresses: 0x00035A70
- Checked: ghidra-mcp disassemble_function by the reviewer (2026-11-24); the matcher's compiles in the worktree of night batch 12 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The original updates the dword at +4, then the dword at +0, each with `and 0xf8; or 8`. A bit-field struct with an inline member `set()`, called as `y.set(); x.set();`, matches at 100%. The direct form `y.a = 0; y.b = 1; x.a = 0; x.b = 1;` gives 23.8%: VC71 loads both dwords first, then stores `[ecx]` and `[ecx+4]`. The reviewer compiled the direct form on nested and on flat structs, with the same result.
- Revisit when: a function of this shape matches only with the direct stores.

## F-0135 The unit of 0x001A5890 holds a second function at 0x001A58A0 that Ghidra has not created
- Status: open
- Addresses: 0x001A5890, 0x001A58A0
- Checked: ghidra-mcp disassemble_function by the matcher, and read_memory, disassemble_function and get_xrefs_to by the reviewer of night batch 13 (2026-11-24)
- Evidence: 0x001A5890 is 16 bytes, `mov eax,ecx; mov [eax],0; mov [eax+4],0; ret`, and Ghidra ends it at 0x001A589F. The unit goes on with `66 8B 41 5E C3` (`mov ax,[ecx+0x5e]; ret`) at 0x001A58A0, where Ghidra has no function. `get_xrefs_to` gives no reference to either address. The source builds 16 of the 21 bytes, 76.2%, and the function is parked as `unclassified`, as F-0128 and F-0130 are.
- Next: create a function at 0x001A58A0, as issue #94 did for F-0124, then match 0x001A5890 and the getter at 0x001A58A0.

## F-0136 0x00189F40 matches with an int field as well as a pointer field
- Status: confirmed
- Addresses: 0x00189F40
- Checked: the matcher's compile in the worktree of night batch 13, and the reviewer's compile of the `int` form in a scratch copy (2026-11-24)
- Evidence: The function is `mov eax,[esp+4]; mov ecx,[ecx+eax*4+0x12c]; cmp [ecx+8],0; setnz al; ret 4`. `return items[i]->v;` with a `bool` return matches at 100% with `void* v` and with `int v`. The matcher reported that only the pointer field matches; the reviewer's compile rejects that claim. The kept source uses the pointer field.
- Revisit when: a function of this shape matches only with one of the two field types.

## F-0137 0x0010EF30 is parked as source shape at 19.0%
- Status: open
- Addresses: 0x0010EF30
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 13 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The function is `movzx eax,word [ecx+2]; dec eax; mov word [ecx+2],0; mov edx,[ecx]; shl eax,16; or edx,eax; mov [ecx],edx; ret`, 21 bytes. The kept form, two 16-bit bit-fields and an `|=` through a cast to `unsigned int*`, gives 19.0% with the first difference at +0x4 and 19 bytes built: VC71 uses `sub`, `shl` and `or [ecx],eax`. The matcher tried five forms (a union with `|=` and with `v = v | ...`, the decrement before the store, word members with a dword cast, bit-fields), and the reviewer compiled five more (a union with `unsigned short hi`, a cast to `unsigned short*`, a bit-field with `hi = t`, a union with an `unsigned short` local, two `unsigned short` members). None gives more than 19.0%.
- Next: find the callers in Ghidra to learn what the dword holds, and try a named class with the two halves and a helper.

## F-0138 The unit of 0x001C4290 holds a second function at 0x001C42A0 that Ghidra has not created
- Status: open
- Addresses: 0x001C4290, 0x001C42A0
- Checked: ghidra-mcp disassemble_function by the matcher, and read_memory, disassemble_function and get_xrefs_to by the reviewer of night batch 14 (2026-11-24)
- Evidence: Ghidra ends 0x001C4290 at 0x001C429D with `RET 4`. The unit goes on with `0F BF 41 10 C3` (`movsx eax,word ptr [ecx+0x10]; ret`) at 0x001C42A0, then `cc` padding. Ghidra has no function at 0x001C42A0 and no reference to it. The source builds 16 of the 21 bytes, 76.2%, and the function is parked as `unclassified`, as F-0130 and F-0135 are.
- Next: create a function at 0x001C42A0, as issue #94 did for F-0124, then match both.

## F-0139 0x00035E30 and 0x001DACD0 end in shr and `and al,1` where every built form gives `and eax,1`
- Status: open
- Addresses: 0x00035E30, 0x001DACD0, 0x0003C02B
- Checked: ghidra-mcp disassemble_function and get_xrefs_to by the matcher and the reviewer of night batch 14; the matcher's compiles in the worktree (2026-11-24)
- Evidence: 0x00035E30 is `mov eax,[eax+0x1c]; shr eax,2; and al,1`, with `xor al,al` on the null path, and its only caller is at 0x0003C02B. 0x001DACD0 ends in `shr eax,1; and al,1`. The matcher tried five forms (a `bool` return, an `unsigned char` return with a cast, a bit-field with a `bool` return and with an `unsigned char` return, an inline accessor), and each built `and eax,1`. The two functions are parked as source shape at 65.2% and 81.8%. The reviewer did not compile other forms. The reviewer states that this is not the `inc` against `add` question of F-0123 or the flag question of F-0018; that a one-bit bit-field of another declared type explains it is a guess.
- Next: compile one-bit bit-field reads of `unsigned char`, `int` and `bool` members at the default flags and compare the bytes.

## F-0140 0x00035700 matches with sqrt declared in the source
- Status: confirmed
- Addresses: 0x00035700
- Checked: the matcher's compile in the worktree of night batch 14; ghidra-mcp disassemble_function by the reviewer (2026-11-24)
- Evidence: The function is `fld; fmul; faddp; fsqrt`, a length of two floats. `extern "C" double sqrt(double);` in the source and `(float)sqrt(x*x + y*y)` match at 100%, with `fsqrt` inline. The build has no include path for `math.h`, as F-0132 records for `memset`.
- Revisit when: the build gets an include path for the CRT headers.

## F-0141 0x0010A4B0 and 0x00119FB0 update a dword after a word store and are parked as source shape
- Status: open
- Addresses: 0x0010A4B0, 0x00119FB0, 0x0010EF30
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 15 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: Both originals store the word `[ecx+2] = 0` and then update the dword `[ecx]`. 0x0010A4B0 loads `[ecx]` into edx, shifts the argument by 16, does `or edx,eax` and stores to `[ecx]`; every form builds `or [ecx],eax` (18 of 22 bytes, 18.2%). 0x00119FB0 does `or dword [ecx],0x80000000`; every form narrows it to `or byte [ecx+3],0x80` (20 of 22 bytes, 13.6%). The matcher tried eight forms for each (a cast, a union, `unsigned short` members, 16-bit bit-fields with a cast as in F-0137, a temporary, local pointers, a signed member, an inline helper), and the reviewer compiled four more for each. This is the shape of F-0137 (0x0010EF30).
- Next: find the callers in Ghidra to learn what the dword holds, and settle F-0137 and this entry together.

## F-0142 Three two-pointer copies match only when they return this
- Status: confirmed
- Addresses: 0x001F2960, 0x001F2A60, 0x001F2C50, 0x001FF190, 0x001FF8C0, 0x001FF8E0, 0x00200720, 0x00205DE0, 0x001FF170, 0x001FF1C0, 0x001FF360
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the reviewer's compile in a scratch copy for 0x001F2960 (2026-11-24); ghidra-mcp disassemble_function and the reviewer's compile of the `void` form of 0x001FF8C0 in night batch 18 (2026-11-24)
- Evidence: Each function is `mov eax,ecx; mov ecx,[esp+4]; mov edx,[ecx]; mov ecx,[esp+8]; mov [eax],edx; mov edx,[ecx]; mov [eax+4],edx; ret 8`. `a = *p; b = *q; return this;` matches all three at 100%. The `void` form with the same stores gives 13.6% for 0x001F2960, with the first difference at +0x1 and 20 bytes built against 22. The other two have the same bytes, and the reviewer did not compile them separately. Night batch 18 matched eight more with `return this;`: 0x001FF170, 0x001FF1C0 and 0x001FF360 copy two ints, and 0x001FF190, 0x001FF8C0, 0x001FF8E0, 0x00200720 and 0x00205DE0 copy an int and then a byte (`mov dl,[ecx]; mov [eax+4],dl`). The `void` form of 0x001FF8C0 gives 13.6%, with the first difference at +0x1; the reviewer compiled it and no other `void` form.
- Revisit when: a function of this shape matches with a `void` return.

## F-0143 A bit-test getter at 0x001EAA90 matches with `? true : false` and not with `!= 0`
- Status: confirmed
- Addresses: 0x001EAA90
- Checked: ghidra-mcp disassemble_function by the reviewer; the matcher's compiles in the worktree of night batch 17 and the reviewer's compile in a scratch copy (2026-11-24)
- Evidence: The function is `mov eax,ecx; mov ecx,[esp+4]; mov edx,1; shl edx,cl; test [eax+0x20],edx; setnz al; ret 4`. `return (m & (1u << n)) ? true : false;` and a `bool` local both give 100%. `!= 0`, `!!` and `!= 0u` give 44.0%, with the first difference at +0x1.
- Revisit when: a bit-test getter matches only with `!= 0`.

## F-0144 0x001F54C0 matches with a pointer member as well as an int member
- Status: confirmed
- Addresses: 0x001F54C0
- Checked: ghidra-mcp disassemble_function by the reviewer; the reviewer's compile in a scratch copy (2026-11-24)
- Evidence: The function is `mov edx,[ecx+0x404]; mov eax,[esp+4]; mov [eax+0x30],edx; mov [ecx+0x404],eax; ret 4`, a push onto the head of a linked list. The kept source, with `int` members and `head = (int)p;`, gives 100%, and so does the form with `N* next; N* head; head = p;`.
- Revisit when: a caller shows the node type; then the pointer form is the better source.

## F-0145 The unit of 0x000335C0 holds a second function at 0x000335D0 that Ghidra has not created
- Status: open
- Addresses: 0x000335C0, 0x000335D0
- Checked: ghidra-mcp disassemble_function and get_xrefs_to by the matcher, and read_memory, disassemble_function and get_xrefs_to by the reviewer of night batch 18 (2026-11-24)
- Evidence: 0x000335C0 is 16 bytes, `mov eax,[ecx]; mov edx,[esp+4]; mov [ecx+eax*4+4],edx; add dword [ecx],1; ret 4`. The unit goes on with `83 39 00 0F 95 C0 C3` (`cmp dword [ecx],0; setnz al; ret`) at 0x000335D0. Ghidra has no function there and no reference to either address. A second method with the address comment 0x000335D0 gives "no target unit starts here". The source builds 16 of the 23 bytes, 69.6%, and the function is parked as `unclassified`, as F-0138 is.
- Next: create a function at 0x000335D0, as issue #94 did for F-0124, then match 0x000335C0 and the new function.

## F-0146 0x001458E0 sets x and z of a 3-float member and matches only through an inline member of the vector
- Status: confirmed
- Addresses: 0x001458E0, 0x001458B0, 0x0006CE60, 0x0006EA90, 0x00075700
- Checked: ghidra-mcp disassemble_function and get_xrefs_to by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 20 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: 0x001458E0 stores two floats from its argument to `[ecx+0x24]` and `[ecx+0x2c]` and then calls slot 20; the original stores `[ecx+0x2c]` before it loads the vtable pointer. The sibling 0x001458B0 copies three dwords to +0x24, +0x28 and +0x2C and then calls slot 20, so +0x24 is a 3-float vector. The callers are 0x0006CE60, 0x0006EA90 and 0x00075700. `pos.setXZ(v); s20();`, with `setXZ` an inline member of the vector struct, matches at 100%, and so does an `operator=` of the vector from a 2-float struct. The direct stores `pos.x = v->x; pos.z = v->y;` give 78.3% with the first difference at +0xC, a `setXZ` on the outer class gives 78.3%, two locals give 18.5%, and z first gives 47.8%; the reviewer compiled these. The reviewer passed the helper under S1 as an ordinary vector member. That the original had such a helper is a guess from the match; the name `setXZ` is a placeholder.
- Revisit when: the vector class of the game is known; then use its real member.

## F-0147 Ten stream helpers are cdecl free functions that return the stream
- Status: confirmed
- Addresses: 0x0012BF50, 0x0012BF70, 0x0012BF90, 0x0012EC80, 0x0012ECA0, 0x00135390, 0x00143690, 0x001520F0, 0x00152110, 0x00152130
- Checked: ghidra-mcp disassemble_function on all ten by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 20 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: Each ends in a plain `RET` after `mov eax,esi`. The write helpers take the value by value and call slot 5 (`call [eax+0x14]`) with its address and a size of 4, 2 or 1. The read helpers pass the pointer argument to slot 4 (`call [eax+0x10]`). `S* f(S* s, T v) { s->w(&v, n); return s; }` and `S* f(S* s, T* v) { s->r(v, n); return s; }` match all ten at 100%. 0x0012BF90 with a by-value `int` gives 47.8%, as `__stdcall` it gives 88.0% with the first difference at +0x16, and 0x0012BF50 with a `void` return gives 0.0%. Which type of each size the helpers take is a guess, because the bytes are the same.
- Revisit when: a caller in Ghidra shows one of these as a member of the stream class.

## F-0148 A range and flag test at 0x00164580 matches with if and two returns, not with one return expression
- Status: confirmed
- Addresses: 0x00164580
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 21 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The function is `cmp [esp+4],8; ja; cmp byte [ecx+4],0; jz; mov al,1; ret 4; xor al,al; ret 4`. `if (n <= 8 && on) return true; return false;` gives 100%. `return n <= 8 && on != 0;` gives 50.0%, with the first difference at +0x6. F-0143 records a similar result for a bit test.
- Revisit when: a function of this shape matches only with one return expression.

## F-0149 A flag-selected array read at 0x001E78A0 matches only with the not-set branch first
- Status: confirmed
- Addresses: 0x001E78A0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 23 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The function is `cmp [esp+8],0; jnz; mov eax,[esp+4]; mov eax,[ecx+eax*4]; ret 8; mov eax,[ecx+8]; ret 8`. `if (!second) return m[i]; return m[2];` gives 100%. `if (second) return m[2]; return m[i];` and `return second ? m[2] : m[i];` give 43.5%, with the first difference at +0x5.
- Revisit when: a function of this shape matches only with the set branch first.

## F-0150 Thirty-three three-argument setters of night batches 19, 22, 23 and 24 share one 23-byte shape
- Status: open
- Addresses: 0x0004AAD0, 0x0004AB00, 0x000797A0, 0x00082B50, 0x000B16E0, 0x000BB320, 0x000D6540, 0x000DCD00, 0x000DF860, 0x000F4E60, 0x001A9660, 0x001B1040, 0x001C29A0, 0x001D81D0, 0x001DB5E0, 0x001DB600, 0x001DB630, 0x001DB670, 0x001DB690, 0x001DB6B0, 0x001EB080, 0x001EB0A0, 0x001EFB70, 0x001F5E40, 0x001F5E60, 0x001F8EB0, 0x001F8ED0, 0x001FD780, 0x00208360, 0x00208380, 0x0020D7C0, 0x0020D8A0, 0x002106F0
- Checked: ghidra-mcp disassemble_function by the matchers and the reviewers of night batches 19, 22, 23 and 24; `uv run python -m bodecomp.match` in their worktrees (2026-11-24)
- Evidence: Each function is `mov eax,[esp+4]; mov edx,[esp+8]; mov [ecx],eax; mov eax,[esp+0xc]; mov [ecx+4],edx; mov [ecx+8],eax; ret 0xc`. `x = a; y = b; z = c;` on a struct of three `int` members matches all 33 at 100%. Whether the members are `int` or `float` is a guess, because the bytes are the same. Nobody compiled another source form.
- Next: add the shape to `bodecomp.trivial` after a reviewer passes one example address (ADR-0013), so that later batches do not spend a matcher on it.

## F-0151 A null-guarded tail call through a member pointer at 0x001FE880 matches only through a local copy
- Status: confirmed
- Addresses: 0x001FE880, 0x000F5070
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 24 and the reviewer's compiles in a scratch copy (2026-11-24); ghidra-mcp disassemble_function and the reviewer's compiles in a scratch copy for 0x000F5070 in night batch 25 (2026-11-24)
- Evidence: The function is `mov ecx,[ecx+0x1d0]; test ecx,ecx; jz; mov eax,[ecx]; jmp [eax+0xa4]; mov al,1; ret 4`. With a local copy `T* p = t;`, both `return p ? p->v41(a) : true;` and `if (p) return p->v41(a); return true;` give 100%. Forms on the member give 17.9% (`if (t) ...` and the ternary) and 14.3% (`if (!t) return true;`), and the local with `if (!p) return true;` gives 43.5%. The reviewer passed the local copy under S1 as ordinary code that caches a pointer it tests and calls through; it is not the store-order reference that F-0117 failed. Night batch 25 found the same result at 0x000F5070, `cmp byte [ecx+0x80],0; jz; mov ecx,[ecx+0x30]; test ecx,ecx; jz; mov eax,[ecx]; jmp [eax+0x14]; ret 4`. With `T* p = t;` inside `if (on)` or after `if (!on) return;` it gives 100%. Six forms that read the member twice give 34.6%, with the first difference at +0x8, and `T* p = t; if (on && p)` gives 19.2%.
- Revisit when: a null-guarded call through a member pointer matches without a local.

## F-0152 A masked table push at 0x00033B00 matches when the masked index is computed once
- Status: confirmed
- Addresses: 0x00033B00
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 25 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: The function is `mov eax,[esp+8]; mov edx,[esp+4]; and eax,0x3f; push esi; mov esi,[ecx+eax*4]; mov [edx],esi; mov [ecx+eax*4],edx; pop esi; ret 8`. `unsigned h = i & 0x3f;` (or `int h`, or `i &= 0x3f;`) followed by `n->next = t[h]; t[h] = n;` gives 100%. The repeated `t[i & 0x3f]` gives 33.3%, with the first difference at +0x4, and so does a pointer `N** s = &t[i & 0x3f];`. The reviewer passed the named index under S1 as the ordinary way to write a hash-bucket push.
- Revisit when: a form with the repeated expression matches.

## F-0153 A call through the second of two virtual bases at 0x000B04B0 matches with the bases declared
- Status: confirmed
- Addresses: 0x000B04B0
- Checked: ghidra-mcp disassemble_function and get_xrefs_to by the matcher and the reviewer; `uv run python -m bodecomp.match` in the worktree of night batch 25 (2026-11-24)
- Evidence: The function is `mov eax,[ecx+4]; mov ecx,[eax+4]; mov edx,[ecx+8]; lea ecx,[edx+eax+4]; mov eax,[ecx]; call [eax+0x1c4]; mov eax,[eax]; ret`: it loads a member pointer, finds the second virtual base through the vbtable at +4, calls slot 113 and returns the int that the result points to. `struct T : virtual V1, virtual V2` with 113 placeholder virtuals in `V2` before the called one matches at 100% with no cast; 112 slots give 95.8%. Ghidra has no reference to the function. F-0131 is another virtual-base conversion that VC71 generates from declared bases.
- Revisit when: the real class is known and the placeholder slots get names.

## F-0154 The units of 0x001AE130 and 0x001AEE40 hold a thunk at 0x001AE140 and 0x001AEE50 that Ghidra has not created
- Status: open
- Addresses: 0x001AE130, 0x001AE140, 0x001AEE40, 0x001AEE50, 0x001AEE60, 0x001A8FD0
- Checked: ghidra-mcp read_memory and disassemble_function by the matcher and the reviewer of night batch 26; `uv run python -m bodecomp.match` in the worktree (2026-11-24)
- Evidence: read_memory at 0x001AE140 gives `2b 49 fc e9 88 ae ff ff` (`SUB ECX,[ECX-4]; JMP 0x001A8FD0`), and at 0x001AEE50 it gives `2b 49 fc e9 08 00 00 00` (`SUB ECX,[ECX-4]; JMP 0x001AEE60`). disassemble_function finds no function at either address. 0x001AEE60 is a function in Ghidra, `MOV AL,[ECX-0xDE]; SHR EAX,5; AND AL,1; RET`. So each unit holds a 16-byte function and then an 8-byte virtual-base thunk, the shape of F-0078 with a thunk in place of a function. Both functions are also F-0120 cases and are parked as source shape at 66.7% and 29.2%. For 0x001AEE40 the matcher reports six forms of `(v & 0x200) >> 9` that all build `shr eax,9; and eax,1` (14 bytes) where the original has `and eax,0x200; shr eax,9`; the reviewer did not compile them.
- Next: create functions at 0x001AE140 and 0x001AEE50, as issue #94 did for F-0124, and claim the thunks with `generated` lines once their targets are matched.

## F-0155 0x00186F10 needs an unsigned member and 0x001A6DD0 needs the not-equal branch first
- Status: confirmed
- Addresses: 0x00186F10, 0x001A6DD0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 26 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: 0x00186F10 is `cmp [ecx+4],0; jz; mov eax,[ecx+8]; add eax,0x1f; shr eax,3; and eax,0x1ffffffc`. With `unsigned n` it gives 100%; with `int n` it gives 95.8%, the first difference at +0xD, because VC71 builds `sar` for `shr`. 0x001A6DD0 is `mov eax,[ecx+0x10]; cmp eax,-1; jz; ...; mov al,1; ret 4; xor al,al; ret 4`. `if (v != -1) { *out = v; return true; } return false;` gives 100%; `if (v == -1) return false; *out = v; return true;` gives 41.7%, the first difference at +0x6. F-0149 records the same branch-order effect.
- Revisit when: a function of either shape matches with the other form.


## F-0156 A masked unsigned char member converts to bool at 0x00071BA0 without a ternary
- Status: confirmed
- Addresses: 0x00071BA0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of the first batch of the run of 2026-11-24 and the reviewer's compiles in a scratch copy (2026-11-24)
- Evidence: Ghidra shows `test byte [eax+0xb6],6; setnz al` after a call to virtual slot 107. With an `unsigned char` member, `return p->FUN_s107()->flags & 6;` as a bool gives the same bytes as the committed `? true : false`. `!= 0` and `!!` give `and al,6; neg al; sbb eax,eax; neg eax` (58.6%). A `char` member or an `unsigned int` member does not match.
- Revisit when: a bool flag test elsewhere gives a different shape.

## F-0157 A string copy into a caller buffer at 0x00033550 is strcpy of a literal
- Status: confirmed
- Addresses: 0x00033550
- Checked: ghidra-mcp disassemble_function and read_memory by the matcher and the reviewer (2026-11-24)
- Evidence: Ghidra shows `rep movsd` of 10 dwords and a `movsw` from 0x002E362C to the argument, with `ret 4`; the string there is 41 characters plus the NUL. `strcpy(out, "...")` with an `extern "C"` declaration matches at 100%, and `memcpy(out, lit, 42)` gives the same bytes. The source declares `strcpy` and `memset` itself, because the matcher has no include path for `<string.h>` (C1034).
- Revisit when: not needed.

## F-0158 A masked unsigned int member converts to bool at 0x00124B00 without a ternary
- Status: confirmed
- Addresses: 0x00124B00, 0x00124B20
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the reviewer's compiles in a scratch copy of the worktree of night batch 2 (2026-11-24)
- Evidence: Ghidra shows `mov edx,1; shl edx,cl; test [eax+0x80],edx; setnz al; ret 4` (+0x84 for 0x00124B20). `return bits & (1 << n);` as a bool gives 100% at 0x00124B00, the same bytes as `? true : false`. `(bits & (1 << n)) != 0` gives 30.0% at 0x00124B20, the first difference at +0x6, and `!!(...)` does not match. The matcher said the ternary is required; the reviewer showed it is not. F-0156 records the same effect for a masked unsigned char.
- Revisit when: a bool flag test elsewhere gives a different shape.

## F-0159 The call at 0x000B0490 needs two virtual bases
- Status: confirmed
- Addresses: 0x000B0490
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the reviewer's compile in a scratch copy (2026-11-24)
- Evidence: Ghidra shows `mov eax,[ecx+4]; mov ecx,[eax+4]; mov edx,[ecx+8]; lea ecx,[edx+eax+4]; mov eax,[ecx]; call [eax+0x1c4]`, which is slot 113 of the second virtual base. A class with `virtual V1, virtual V2` matches at 100%. With only `virtual V2` it gives 96.0%, the first difference at +0x8. F-0153 is the same function shape at another address.
- Revisit when: the real class is known.

## F-0160 Reordering the stores does not fix the scheduling parks at 0x000D67D0 and 0x000D67F0
- Status: open
- Addresses: 0x000D67D0, 0x000D67F0, 0x000D9AE0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; compiles in the worktree of night batch 2 and in a scratch copy (2026-11-24)
- Evidence: The original orders `or byte [p+0x5b],0x10`, the `movss` store at +0x54 (+0x60 pointer for the second), then `or dword [p+8],2`. VC71 puts the `movss` store last in all variants: six statement orders, a local pointer copy, bitfields, member helpers and a float temporary. The scores are 64.0% and 60.0%. 0x000D9AE0 shows the same shape with an int store. No donor score was found, so the check of F-0093 is not done.
- Next: look for a GameCube donor of the class and score its form.

## F-0161 0x0012EC50 is an inline fsin and fcos pair that sinf and cosf calls do not match
- Status: open
- Addresses: 0x0012EC50, 0x0011E4B0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compile in the worktree of night batch 2 (2026-11-24)
- Evidence: The original is `fld; fsin; fstp` and `fld; fsin`-style `fcos` pairs with float loads and stores. `sinf` and `cosf` compile to calls and give 2.9%. No source form without inline assembly (ADR-0013) is known that emits the x87 instructions. Night batch 3 of 2026-11-25 parked 0x0011E4B0 as source shape at 0%: `fld [esp+4]; fldl2e; fmulp; fld st0; frndint; fxch; fsub; f2xm1; fld1; faddp; fscale; fstp st1; ret`, an inline x87 exp (an inference from the instructions), which a call to `expf` does not build (disassemble_function by the matcher and the reviewer, 2026-11-25).
- Next: check the SDK math headers for an inline form.

## F-0162 Three compiler-form claims of night batch 3 at 0x001A85A0, 0x001550A0 and 0x001B0DB0
- Status: confirmed
- Addresses: 0x001A85A0, 0x001550A0, 0x001B0DB0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the matcher's compiles in the worktree of night batch 3 and the reviewer's compiles with `/O2 /G7 /arch:SSE /GX` in the same worktree (2026-11-24)
- Evidence: 0x001A85A0 reads `[ecx-0x68]` with no null test. `static_cast<D*>(this)` for `D : Base, S` emits `test ecx,ecx; je; lea eax,[ecx-104]; xor eax,eax` (35 bytes against 32), and `((Base*)((char*)this - 0x68))->owner` matches at 100%. 0x001550A0 walks a list with no test at entry: `for` and `while` forms emit a leading `test ecx,ecx; je` (the `while (s != p)` form scores 41.4%), and the do-while form matches. 0x001B0DB0 needs `if (a) return ((a - b - 1) & 3) + 1; return 0;` with unsigned arguments; `if (!a) return 0;` first scores 24%. The ternary `a ? expr : 0` gives the same layout as the matching form.
- Revisit when: the class layout around 0x001A85A0 is known.

## F-0163 A bool compare of a virtual call at 0x0021D9A0 needs a local bool
- Status: confirmed
- Addresses: 0x0021D9A0
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the reviewer's scratch compile with `/O2 /G7 /arch:SSE /GX` (2026-11-24)
- Evidence: The original is `cmp eax,esi; setz al`. `return slot(a,b) == b;` builds `xor ecx,ecx; cmp eax,esi; sete cl; mov al,cl` (55%), and `- b == 0` builds `sub/neg/sbb/add` (58%). `bool r = slot(a,b) == b; return r;` matches at 100%. This differs from F-0156 and F-0158, where a plain conversion works.
- Revisit when: a bool compare of a call elsewhere builds the other shape.

## F-0164 Setting or clearing one flag bit at 0x0005D630 needs the ternary form
- Status: confirmed
- Addresses: 0x0005D630
- Checked: ghidra-mcp disassemble_function by the matcher and the reviewer; the reviewer's scratch compiles with the default flags (2026-11-25)
- Evidence: The original loads the flags into EAX once, then branches to `or al,1` or `and al,0xfe`. `flags = on ? (flags | 1) : (flags & ~1u);` matches at 100%, and so does a local copy of the flags. `if (on) flags |= 1; else flags &= ~1u;` gives 19.2% (first difference at +0x5), and `flags = (flags & ~1u) | (on ? 1 : 0);` gives 0.0%.
- Revisit when: a flag member at another address matches with the `if`/`else` form.
