# ADR-0018: The milestones are renumbered, and GitHub milestones group the issues

- **Status:** Accepted (user decision, 2026-11-15; M5's name and exit condition approved with the plan of issue #20, 2026-11-17)
- **Date:** 2026-11-17

## Context

The milestone tables in `docs/STATUS.md` and `docs/METHODOLOGY.md` defined M5 as the recomp harness and M6 as the layout. The maintainer started M5 with the thunk trial of issue #1 instead (`docs/intent/repo-overhaul.md`). The trial's outcome is "no gain" (F-0110, `docs/thunk-trial-results.md`). It sends the next work to the search for the next byte shape among larger functions.

The work moved to GitHub issues (ADR-0014). Issues need a way to show the milestone they serve.

## Decision

- M5 is "M5 Larger functions". Its exit condition: a byte shape among functions larger than the gen_trivial set is found, and one matcher batch of that shape merges through the full gate, with its cost per matched function recorded. Issues #1 to #10, the thunk trial, are in M5.
- The harness becomes M6, and the layout becomes M7. Their exit conditions do not change.
- GitHub milestones M0 to M7 group the issues. M0 to M4 are closed. Each description gives the exit condition and links the milestone's results file when it has one.
- The milestone table in `docs/STATUS.md` stays the record of each exit condition and result. The table in `docs/METHODOLOGY.md` has the same rows.
- Work on the repo itself, such as issue #20, is in no milestone, because the milestones measure the decomp.

## Consequences

- A text that says "M5" before 2026-11-17 and means the harness, such as an older results file, now means M6.
- `tests/test_docs.py` fails when the milestone rows of `docs/STATUS.md` and `docs/METHODOLOGY.md` differ in number or name.
- GitHub milestone state has no test. A change to it gives the `gh` command and its output in its pull request.
