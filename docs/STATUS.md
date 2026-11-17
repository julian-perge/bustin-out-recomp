# Status

The milestone table. The state of the work (branch, running processes, Ghidra writer, pull requests, assigned issues, next command, last merged pull request, open findings) is not kept here. `tools/session-start.sh` prints it from git, GitHub and `docs/FINDINGS.md` at each session start (ADR-0021). Details belong in result documents, `docs/FINDINGS.md` and `docs/adr/`.

## Milestones

| Milestone | Exit condition (`docs/METHODOLOGY.md`) | Status |
|---|---|---|
| M0 Toolchain | 20 hand-written leaf functions match with a recorded flag set | Passed 2026-10-10 at 19 of 20 ([m0-results](m0-results.md)) |
| M1 Analysis | Ghidra rebuilds from text, SDK named, re-link reproduces `.text`, raw findings re-checked | Passed, merged 2026-10-11 ([m1-results](m1-results.md)) |
| M2 Naming | First naming pass, named share reported per tier | M2a passed 2026-10-11; M2b passed 2026-10-12 (497 string names); `gc` naming deferred (F-0029). M2 complete 2026-10-12 (user ruling) ([m2-results](m2-results.md)) |
| M3 First batch | One matcher batch merged through the full gate | Passed 2026-10-12: two batches, 20 matched and 1 parked ([m3-results](m3-results.md)) |
| M4 Steady state | Batches run routinely, progress tracked | Passed 2026-10-12: gen_trivial kept 2246 of 2246, three batches matched 57 of 60, 2324 matched in all ([m4-results](m4-results.md)) |
| M5 Larger functions | A byte shape among functions larger than the gen_trivial set is found, and one matcher batch of that shape merges through the full gate, with its cost per matched function recorded | Started 2026-11-14 with the thunk trial (#1), whose outcome is no gain (F-0110, [thunk-trial-results](thunk-trial-results.md)) |
| M6 Harness | Rebuilt XBE byte-identical; harness reaches the main menu | Not started |
| M7 Layout | Source-file splits and data matching under way | Not started |
