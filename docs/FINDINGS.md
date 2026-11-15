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
- Addresses: 0x0015D6C0, 0x0015D6D0, 0x00165F20, 0x00165F30
- Checked: ghidra-mcp, matcher and reviewer of M4 batch 3 (2026-10-12)
- Evidence: Units come only from the `function` starts in config/symbols.txt (bodecomp/split.py), so a start that is missing there makes the unit before it too long. The unit 0x0015D6C0-0x0015D6E0 is `c3`, 15 bytes of `cc`, and a second `c3` at 0x0015D6D0. Ghidra sizes FUN_0015d6c0 at 1 byte with no references, and 0x0015D6D0 belongs to FUN_001235c0, whose jump at 0x00123633 reaches it, so it is a shared return of another function and not a function of its own. The unit 0x00165F20-0x00165F40 is a 16-byte body followed directly by `c3` at 0x00165F30. Ghidra sizes FUN_00165f20 at 16 bytes and has no function at 0x00165F30, but a data reference from the table slot 0x002EED88 points at it, so it is a 1-byte function that is missing. Both units are parked as `unclassified` (5.9% and 94.1%). The reviewer's raw scan for non-padding bytes after a run of `cc` inside a unit found 15 units, including 0x000DC8F0, 0x00157EE0, 0x001BEEA0, 0x0020C750 and 0x00242660; that list is preliminary (ADR-0003), may include int3 bytes inside functions (F-0028, F-0075) or known gaps (F-0026), and cannot see the 0x00165F20 case, which has no `cc` run.
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
- Next: find why the 47 other vtable-store functions do not match; the byte check above predicts 41 of them.

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
- Checked: ghidra-mcp disassemble_bytes on 0x00047CE0, disassemble_function on 0x000474C0, 0x00047ED0 and 0x00047520, read_memory on 0x002E3A60, 0x002E3AC0 and 0x002E38F0 (2026-11-15); a test compile of a class 1 skeleton at `/O2 /G7 /arch:SSE`, run through `bodecomp.match.check_source` (2026-11-15)
- Evidence: The probe of issue #4 compiled a scratch skeleton, `class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0`, with the constructor, the destructor and four overrides (`docs/thunk-trial-results.md`). VC71 emitted `2b49fc81e9ec000000e9` with a REL32 relocation to the deleting destructor for slot 0 of the virtual base's vtable, and `2b49fce9` with a REL32 relocation to the override for slots 1 and 2. These are the bytes at 0x00047CE0, 0x00047CF0 and 0x00047D00, and `/GX` does not change them. `check_source` reported the destructor 0x000474C0 and the overrides 0x00047520 and 0x00047D10 as `matched`. The destructor's match compares both vtables, the three thunks and the 40-byte deleting destructor 0x00047ED0 with the original. Three facts about the class came out of the compile. The destructor of the virtual base is inline in its class: with a declaration only, the built deleting destructor calls that destructor, and with an inline body it stores the vtable 0x002E38F4 as the original at 0x00047ED0 does. The class has only two members of its own, 8 bytes at +0x4C and a table of 12 pointers to member functions at +0x58, 12 bytes each (the donor's `Unk8003AA6CDraw unk54[12]`): with only these two declared, the virtual base is at +0xEC and the vbtable is `bcffffffa8000000` as at 0x002E3AC8, and two more `int` members at +0x48 and +0x54 moved the virtual base to +0xF4. So the gaps at +0x48 and +0x54 are padding. That VC71 aligns a pointer to a member function of this class to 8 bytes is a guess from the offsets of one test compile. The overrides receive `this` as a pointer to the virtual base, so the 8-byte thunks hold no fixed offset.
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
- Checked: test test_claimed_thunk_with_a_matched_target_is_matched, test test_claimed_thunk_whose_target_is_nonmatching_is_not_matched, test test_claim_that_the_check_never_reached_is_an_error, test test_generated_code_is_equal_when_a_later_check_that_reached_it_passed; test compiles of the class 1 skeleton of issue #4 with `generated` lines, run through `bodecomp.match.check_source` and `settle_jumps` (2026-11-15); `uv run python -m bodecomp.match --check` (2026-11-15)
- Evidence: Issue #5 added the line `// generated: 0xADDRESS` (`docs/WORKFLOW.md`, "Matching"). In a VC71 object at the default flags each vtordisp thunk is a COMDAT `.text` section of its own. The slot of the virtual base's vtable names it with a DIR32 relocation, and its REL32 jump names the override, or `??_E` for slot 0. So a claim's row comes from a check that a function with an address comment starts. With lines for 0x00047CE0, 0x00047CF0, 0x00047D00 and 0x00047ED0, the skeleton of F-0087 gives four `matched` rows, and a line for 0x00047EC0 gives `error`. With another body for the override 0x00047520, the row of 0x00047CF0 is `nonmatching` with "its jump target 0x00047520 is nonmatching". Without the line for 0x00047ED0, the row of 0x00047CE0 is `nonmatching` with "its jump target 0x00047ED0 is not claimed". `config/functions.csv` is unchanged at 3306 matched. The maintainer chose three limits on 2026-11-15. A thunk is any claimed function that ends in a jump, so a generated function with a tail jump also needs a matched target. One check fails as a whole, so a claimed function is `nonmatching` when an item beside it differs and no other check that reached it passed. The tool does not reject a line on an exception-handling funclet or handler, so that rule is in `docs/WORKFLOW.md` only. A `nonmatching` row of a claim has no score, because the resolver stops at an item's first difference.
- Revisit when: a claimed function with a tail jump cannot match because of its target's row, or a source claims a funclet or a handler.
