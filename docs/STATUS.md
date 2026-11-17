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
| M5 Larger functions | A byte shape among functions larger than the gen_trivial set is found, and one matcher batch of that shape merges through the full gate, with its cost per matched function recorded | Started 2026-11-14 with the thunk trial (#1), whose outcome is no gain (F-0110, [thunk-trial-results](thunk-trial-results.md)) |
| M6 Harness | Rebuilt XBE byte-identical; harness reaches the main menu | Not started |
| M7 Layout | Source-file splits and data matching under way | Not started |

## Active

<!-- active:start -->
- Branch: `docs/20-repo-overhaul` for issue #20, from `main` at 85ded1a, with one commit per task #21 to #28 (`/agent-skills:build auto`). It adds `CODING_STANDARDS.md` (rules S1 to S4), the pull request template, three issue forms, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `docs/CODE_MAP.md`, `docs/SUBSYSTEMS.md`, `tests/test_docs.py`, ADR-0018 and ADR-0019, and brings `docs/METHODOLOGY.md` up to date. GitHub milestones M0 to M7 exist, M0 to M4 are closed, and #1 to #10 are in M5 Larger functions. The backlog of this file is now issues #30 to #53, labeled `needs-triage`.
- Running: the ghidra-mcp headless server on port 8089, started again by the lead session on 2026-11-14 after the delink for issue #2. It runs on Ghidra 12.2 with ghidra-mcp built from the `dev` branch at 5f6c416f.
- Owners: lead. Ghidra writer: none.
- Evidence: on 97345b1, `uv run pytest -q` gave 349 passed, `uv run python -m bodecomp.findings check` gave 110 findings and no problems, and `uv run python -m bodecomp.match --check` gave 3363 matched, 0 nonmatching, 5 parked and 0 error. `git diff --name-only 6671bba..HEAD -- src bodecomp tools config` prints nothing. The triage list (`gh issue list --label needs-triage`) shows 24 issues, #30 to #53, 23 of them in M5 and #34 in no milestone.
- Blockers: none.
- Next action: review and merge the pull request of issue #20; it closes #21 to #28. After the merge, check that `gh api repos/julian-perge/bustin-out-recomp/community/profile --jq '.files.contributing.url, .files.pull_request_template.url'` prints two URLs. Then triage #30 to #53, and open an issue for the search for the next byte shape among larger functions, the main work of M5 (ADR-0018). F-0056, F-0059 and F-0071 stay open.
<!-- active:end -->
