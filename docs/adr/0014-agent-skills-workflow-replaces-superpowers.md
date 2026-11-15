# ADR-0014: The repo moves to the agent-skills workflow, and the superpowers documents are retired

- **Status:** Accepted (user decision)
- **Date:** 2026-11-14

## Context

The repo was built with the superpowers flow. Its design specs and plans were in `docs/superpowers/`, and a gitignored ledger in `.superpowers/sdd/` held each plan's rulings (ADR-0007). On 2026-11-14 the user decided to publish the repo on GitHub for outside contributors and to run the work on the agent-skills stages, with GitHub issues as the tracker. `docs/intent/repo-overhaul.md` holds the confirmed statement and the work that is still to do. In that workflow a spec is `spec/<issue>-<slug>.md` and a plan is the sub-issues of its source issue, so the superpowers documents have no place in it.

## Decision

- The repo is published on GitHub, and the work runs on the agent-skills stages with GitHub issues as the tracker.
- The seven finished plans (M0 to M4 and the agent workflow) are removed from the tree. Their outcomes are in the `docs/m*-results.md` files, `docs/FINDINGS.md` and this directory. The result files no longer link to the plans.
- The design spec of 2026-10-10 becomes `docs/METHODOLOGY.md`, the method document. Where an older record says "the design spec", it means that file.
- The agent-workflow design of 2026-10-11 is removed. ADR-0007 holds its decisions. Three of its rules were written nowhere else and continue here:
  - The agent entry file stays at or under 100 lines.
  - The SessionStart hook prints at most 40 lines.
  - The project permissions approve in advance only the read-only ghidra-mcp tools, `tools/session-start.sh` and `tools/ghidra-mcp-headless.sh`. `tools/rebuild-ghidra.sh` and `tools/delink.sh` still ask.
- This supersedes one rule of ADR-0007: the rulings of a finished plan no longer move from the ledger to ADRs or findings, because there is no ledger. A decision is recorded as an ADR when it is settled.
- No tracked file names a user's home directory. `tests/test_machine_paths.py` checks this.

## Consequences

- `AGENTS.md`, `README.md`, `docs/WORKFLOW.md` and `docs/STATUS.md` point to `docs/METHODOLOGY.md`.
- `docs/METHODOLOGY.md` still describes parts of the 2026-10-10 design that the repo did not adopt. Its first section lists them, and the contributor docs of the overhaul must bring it up to date.
- `.superpowers/` and `.recall/` are local scratch that git ignores. Nothing in the repo reads them.
- The other decisions of ADR-0007 stand until a later ADR changes them. ADR-0015 makes `AGENTS.md` the agent entry file.
