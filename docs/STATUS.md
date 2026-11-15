# Status

The milestone table and the handoff to the next session. After each batch, replace the Active block; do not add to it, because git history keeps the old ones. Keep this file under about 60 lines. Details belong in result documents, `docs/FINDINGS.md` and `docs/adr/`.

## Milestones

| Milestone | Exit condition (`docs/METHODOLOGY.md`) | Status |
|---|---|---|
| M0 Toolchain | 20 hand-written leaf functions match with a recorded flag set | Passed 2026-10-10 at 19 of 20 ([m0-results](m0-results.md)) |
| M1 Analysis | Ghidra rebuilds from text, SDK named, re-link reproduces `.text`, raw findings re-checked | Passed, merged 2026-10-11 ([m1-results](m1-results.md)) |
| M2 Naming | First naming pass, named share reported per tier | M2a passed 2026-10-11; M2b passed 2026-10-12 (497 string names); `gc` naming deferred (F-0029). M2 complete 2026-10-12 (user ruling) ([m2-results](m2-results.md)) |
| M3 First batch | One matcher batch merged through the full gate | Passed 2026-10-12: two batches, 20 matched and 1 parked ([m3-results](m3-results.md)) |
| M4 Steady state | Batches run routinely, progress tracked | Passed 2026-10-12: gen_trivial kept 2246 of 2246, three batches matched 57 of 60, 2324 matched in all ([m4-results](m4-results.md)) |
| M5 Harness | Rebuilt XBE byte-identical; harness reaches the main menu | Not started |
| M6 Layout | Source-file splits and data matching under way | Not started |

## Active

<!-- active:start -->
- Branch: `chore/2-create-purecall-and-0003c620-functions`, pull request #11 for issue #2: 5b3503a, the findings commit and the review fixes on top of the first public commit. The review of 2026-11-15 found no blocker. It needs a merge commit, because F-0082 and F-0083 cite 5b3503a (ADR-0016). No worktrees.
- Running: the ghidra-mcp headless server on port 8089, started again by the lead session on 2026-11-14 after the delink for issue #2. It runs on Ghidra 12.2 with ghidra-mcp built from the `dev` branch at 5f6c416f.
- Owners: lead. Ghidra writer: none.
- Blockers: none.
- Backlog: make `tools/delink.sh` or `bodecomp.relink` notice a units list that is older than `config/symbols.txt` (F-0085); 16 bytes of code at 0x0021F748 have no function (F-0082); `tools/rebuild-ghidra.sh` is not yet run on Ghidra 12.2, where ghidra-xbe is built from source at b5171ca (a scratch import and analysis of `default.xbe` passed); look at the 47 vtable-store functions the third gen_trivial pass did not keep (F-0080); name the `ERRleTexture` and similar operator new functions now that operator names are spelled mangled (F-0032); a namer pass to create 0x00165F30 and fix 0x00013730's size (F-0075, F-0078), then check the other units F-0078 lists; try other flags for Apt functions if they fail at the default (F-0021), which needs per-file flags in `bodecomp.match`; redo the M2c pairing when F-0029's revisit condition holds; test the same-file call path on a pair that is not inlined.
- Next action: merge pull request #11 with a merge commit, then build issue #3 with `/agent-skills:build 3` in a new session. Then open an issue for the rest of the repo overhaul from `docs/intent/repo-overhaul.md` and run `/agent-skills:spec` on it (ADR-0014). The contributor docs, the reader docs and the standards doc are not written. The M5 thunk trial is issue #1, with the spec `spec/1-virtual-base-thunk-trial.md` and the plan in sub-issues #2 to #10. Issue #2 is built: `__purecall` at 0x0021F734 and FUN_0003c620 exist (F-0082, F-0083), delinker v0.9.3 passed the `unitsplit --compare` check (F-0084), and the units were cut again (19,797 units, re-link gate 0, 0 and 0). Issue #3 is the next task of the trial with no blocker. 3306 functions are matched: the third gen_trivial pass kept 3227 of 3274, and operator delete at 0x000136E0 is matched by hand (F-0081). F-0056, F-0059 and F-0071 stay open.
<!-- active:end -->
