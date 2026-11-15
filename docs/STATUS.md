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
- Branch: `main`. This commit starts the public repo. It has no parent, and the private history stays on the maintainer's machine (ADR-0016). No worktrees.
- Running: the ghidra-mcp headless server on port 8089 (`tools/ghidra-mcp-headless.sh`), on Ghidra 12.2 with ghidra-mcp built from the `dev` branch at 5f6c416f.
- Owners: lead. Ghidra writer: none.
- Blockers: none.
- Backlog: `tools/rebuild-ghidra.sh` is not yet run on Ghidra 12.2, where ghidra-xbe is built from source at b5171ca (a scratch import and analysis of `default.xbe` passed); look at the 47 vtable-store functions the third gen_trivial pass did not keep (F-0080); name the `ERRleTexture` and similar operator new functions now that operator names are spelled mangled (F-0032); a namer pass to create 0x00165F30 and fix 0x00013730's size (F-0075, F-0078), then check the other units F-0078 lists; try other flags for Apt functions if they fail at the default (F-0021), which needs per-file flags in `bodecomp.match`; redo the M2c pairing when F-0029's revisit condition holds; test the same-file call path on a pair that is not inlined.
- Next action: open an issue for the rest of the repo overhaul from `docs/intent/repo-overhaul.md` and run `/agent-skills:spec` on it (ADR-0014). The contributor docs, the reader docs and the standards doc are not written. The agent-skills workflow is set up (`docs/agents/workflow.md`, ADR-0015). The M5 thunk trial is issue #1, with the spec `spec/1-virtual-base-thunk-trial.md` and the plan in sub-issues #2 to #10. Issue #2 is built on its branch and comes in as the first pull request. 3306 functions are matched: the third gen_trivial pass kept 3227 of 3274, and operator delete at 0x000136E0 is matched by hand (F-0081). F-0056, F-0059 and F-0071 stay open.
<!-- active:end -->
