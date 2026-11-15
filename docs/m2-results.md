# M2 results

M2 is split into M2a (function discovery and the per-tier ledger), M2b (`string`-tier names) and M2c (`gc`-tier names from the GameCube and Sims 2 symbols), by user decision on 2026-10-11.

## M2a: function discovery

All numbers come from the runs on 2026-10-11 on branch `m2a-functions`. The final review of the first run found functions that started inside real code, so discovery was rerun from the M1 symbols with a corrected script; the numbers below are from the rerun unless marked.

- Before: 7,453 gaps in `.text` holding 669,247 bytes, of which 510,274 are not `0xCC` padding (`uv run python -m bodecomp.gaps report`). The report measures against `symbols.txt`, where a size counts the addresses of a function's body; a span is cut at the next function start, so a body split into separate ranges is only approximated. `find_code_gaps` counts 7,982 gaps because it measures Ghidra's bodies.
- Candidates: 11,536 16-byte-aligned addresses after `0xCC` padding (`uv run python -m bodecomp.gaps candidates`).
- Created: 11,489 functions, 12 candidates already inside a function, 34 rejected: 12 `mid-instruction`, 7 `falls-through`, 10 bad-instruction, 4 no-function, 1 data. Auto-analysis afterwards made more functions from call targets and pointer tables: Ghidra went from 10,311 to 21,867 functions (the ledger's 21,731 leaves out external functions).
- Why the rerun: a `0xCC` byte is not always padding. In the first run, 0x001D9880 became a function although it is the immediate byte of `or ah,8` inside the real function at 0x001D9870, which was rejected instead (checked in Ghidra: `FUN_001d9880` decoded as `or byte ptr [ecx+0x4c22041],cl; add ah,cl; int3`). Others, such as 0x00014AE0 after `movaps xmm1,xmm4` (`0F 28 CC`), split a function where its code simply continues. The script now disassembles the candidates from the lowest address up and rejects one inside an instruction of lower code (`mid-instruction`), and after analysis removes a new function that the instruction before it falls through to (`falls-through`). Compared with the first run, 17 such functions are gone and 27 real starts are new, among them 0x001D9870, 0x001BFBD0 and 0x001C4270.
- Two more script fixes came out of the first run. Ghidra's analysis had disassembled from constants that look like code addresses (0x00011102 is used as a constant by `FUN_00185410`), leaving instructions that start inside real ones; the script clears instructions outside every function and disassembles once more. A rejected address that analysis later makes a function start no longer counts as rejected.
- The rejects: 21 of the 34 are inside functions after analysis, which includes all 19 `mid-instruction` and `falls-through` rejects except 0x000C3BF0, whose preceding code is in no function. 13 remain outside any function: 0x00075200, 0x000C3BF0 (falls-through), 0x000DCCB0 (data), 0x000E10C0, 0x000E3DC0, 0x000E3E00, 0x000E4C50, 0x00158140, 0x00193210, 0x001BEF10, 0x001C5D50 (no-function), 0x00242310 and 0x00242680; the ones without a reason are bad-instruction. Checked with ghidra-mcp in the first run: 0x00242680 and 0x000E3E00 have a normal prologue and a DATA reference from a pointer table, and 0x000DCCB0 has a DATA reference from a pointer table with ordinary code from +6. Why the bad-instruction ones fail is not known (F-0026).
- After: 18,854 gaps holding 273,871 bytes, of which 115,169 are not padding (down 77%). Most gaps are now padding only (16,407). The largest remaining gaps by non-padding bytes are 0x0009C68A-0x0009EAB0 (9,240), 0x0001F4C0-0x00020EF0 (6,689) and 0x000C314A-0x000C4070 (3,861).
- SDK names: the new functions include library code. `libmatch` named 2,158 functions (2,007 before) and found 459 ambiguous ones (431 before).
- Rebuild from text: `tools/rebuild-ghidra.sh` created 11,555 functions from `symbols.txt` on top of the import's 10,175 listed starts, rejected 0 (it now also requires every listed start to end up as a function start), and ended at 21,867 functions. `sync check` reports 0 name differences, 0 missing and 0 not in `symbols.txt`.
- Re-link gate: 19,794 units (8,270 before), 0 mismatched bytes, 0 unresolved names, 0 unit problems. The delink took 81 minutes. Two re-links failed first, both on XBE-loader labels that sit on untyped bytes and that the sync cannot see (F-0010). In the first run, `XAPILIB::g_DeviceType_MU` at 0x002D9DC0 was missing from `symbols.txt`; the code that references it had just become a function. In the rerun, `sync export` ran on a freshly rebuilt project before `sync apply`, so Ghidra did not list the four F-0010 labels and the export dropped them. All four are back in `symbols.txt`, and `sync export` now keeps a named data entry that Ghidra does not list.
- xboxrecomp cross-check: of its 16,771 `.text` function starts, 16,694 are now Ghidra functions and 77 are not.
- Ledger: 21,731 functions, of which 18,893 are game functions with automatic names. No game function is named yet: `gc` 0 and `string` 0 (`docs/LEDGER.md`).

## M2c spike: how good is the GameCube evidence

Run on 2026-10-11 against daftblazer/bustin-out-decomp d8483a60 (F-0029). The question: how many Xbox game functions can take a GameCube name with two independent kinds of evidence, and how often is such a pairing wrong. The scripts were throwaway and live in `~/tmp/2026-10-11-m2c-spike`, outside the repo.

Method:

- `main.dol` came from the user's USA ISO; its SHA-1 matches daftblazer's `config.yml` (26f0bf31...). It was converted to an ELF with daftblazer's function symbols and analyzed in a separate Ghidra project as `PowerPC:BE:32:default`, with r2 = 0x803933E0 and r13 = 0x803833E0 from `__start`. Ghidra 12.1.4 has no Gekko language, so paired-single instructions do not decode.
- A Ghidra script listed each function's string references and calls on both platforms; the Xbox project was opened read-only.
- Anchor pairs: an Xbox and a GameCube function that both reference a string no other function on either side references, with no conflicting votes.
- Call-graph support: an anchor pair whose callers or callees include another anchor pair.
- Propagation: the callees of a known pair are paired by call order when both make the same number of distinct calls.

Results:

| Measure | Count |
|---|---|
| Xbox game functions (not `sdk`) | 18,893 |
| Xbox game functions that reference a string | 697 |
| GameCube functions | 10,870 |
| GameCube functions with a full name in daftblazer's `symbols.txt` | 517 |
| GameCube functions with only a class name (`fn_800056C8__8ESimsCam`) | 415 |
| Strings referenced on both platforms | 1,437, of which 1,116 by one function on each side |
| Anchor pairs (all on Xbox game functions, no conflicts) | 271 |
| Anchor pairs with call-graph support | 130 |
| Anchor pairs with a full GameCube name | 13 (14 more with a class name only) |
| Pairs added by propagation | 460 (23 with a full name, 48 with a class name only) |

- The Xbox release has few strings: a raw count of `push imm32` operands that point at strings finds 1,054 distinct strings (preliminary), against 2,387 in Ghidra's references, so Ghidra is not missing many.
- Hand check of 20 random anchor pairs, comparing Ghidra's decompilation on both sides: 19 fit the same function: they share their anchor strings and have similar sizes and call counts, except where one compiler inlines. Three were read in full; the other 17 were compared by strings, size and call count only. For example, 0x000CA090 compares strings inline where the GameCube's 0x800CB260 calls a compare function. One pair is the same source file but a different function: 0x002420F0 is an MSVC initializer for one global (`LightingTweak.txt`), while 0x801853F0 is GCC's initializer for the whole file. Static initializers therefore need to be excluded before a name is carried over.
- Propagation precision is unsettled. Seeded with half the anchors, it reached 6 of the held-out anchors and agreed with 2. Of the propagated pairs where both sides reference strings, 18 of 19 share one. Both samples are small.

Conclusion: string anchors pair functions accurately, and half of them reach two kinds of evidence, but they yield only 13 full names today. The ceiling comes from the donor: daftblazer names 517 of 10,870 functions, so a `gc` naming pass now would name well under 1% of the Xbox game functions. The pairing is worth keeping as an Xbox-to-GameCube address map, because daftblazer's names and matched C++ attach to it as they grow. The Sims 2 map (36,913 symbols) was not tested, because its binary is not available.

## M2b: string names

Rules: ADR-0007 and ADR-0008. After M2b, names come from matching (ADR-0009).

| Measure | Count |
|---|---|
| Game functions that reference a string (`build/strings.tsv`) | 718 (M2c counted 697 with its own spike export; why the two counts differ was not checked) |
| Named from a stated `Class::Method()` string | 6 |
| Named by namers (15 batches and a follow-up pass) | 492 |
| Skipped by namers | 246 |
| Changed or cleared by the reviewer | 29 (2 cleared) |
| Named by the lead in Task 7 (GetLoadBarVariable, F-0040) | 1 |
| `string` tier in the ledger | 497: 2.3% of functions, 10.7% of bytes |

- The 497 string names are the 6 stated names, plus the 492 namer names less the 2 the reviewer cleared, plus the one set in Task 7. A function skipped in one batch and named in the follow-up pass counts in both rows.
- Re-link with the new names: units 19794, mismatched bytes 0, unresolved names 0, unit problems 0.
- Skipped functions, by reason. Batches 1 to 8 recorded only their named functions, so these counts cover the 105 skips listed in batches 9 to 15. The grouping is the lead's reading of the namers' one-line reasons:
  - 41: the only strings are generic, a format, an error message, a file extension or a placeholder such as "<error>", and none says what the function does.
  - 19: the string covers one case or one step of a larger function, such as a message dispatcher.
  - 18: the only string is an `operator new` or allocator tag (F-0032, F-0033, F-0061).
  - 14: the strings do not settle the function's role.
  - 7: library code (CRT math and printf cores), a string fragment, or data read as text.
  - 5: the only string is a source file path.
  - 1: the function already had a name.
- Three functions Ghidra lacked were created in Task 7: 0x975F0 again as one function (F-0040), 0xADA10 (F-0043) and 0x9C6B0 (F-0065). The last two reference no string and keep their auto names (ADR-0009).
- Rounds after batch 8 used Sonnet namers and reviewers after batches 4 to 8 used up a 5-hour usage window in about an hour (ADR-0010).
