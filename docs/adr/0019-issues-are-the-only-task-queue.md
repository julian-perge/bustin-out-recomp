# ADR-0019: GitHub issues are the only task queue, and STATUS holds no backlog

- **Status:** Accepted (user decision, 2026-11-15; the list of issues approved with the plan of issue #20, 2026-11-17). The Active block is removed by [ADR-0021](0021-generated-session-state-and-ghidra-freshness.md)
- **Date:** 2026-11-17

## Context

The work moved to GitHub issues (ADR-0014). The Active block of `docs/STATUS.md` still had a Backlog line. By 2026-11-15 it held 24 items in one paragraph, from rules for the agents to single functions to match. One item could not be claimed, labeled, put in a milestone or closed. The same work could sit both in an issue and in the Backlog line.

The Active block also had no fixed place for the proof of the last batch's state. Rule `S2` of `CODING_STANDARDS.md` asks for that proof.

## Decision

- GitHub issues are the only task queue. Work that is noticed and not done becomes an issue labeled `needs-triage`.
- `docs/STATUS.md` holds no backlog. Issue #28 moved each item of the Backlog line at commit 6671bba to its own issue, #30 to #53. Each body holds the item's text, its finding IDs and that commit.
- The fields of the Active block are Branch, Running, Owners, Evidence, Blockers and Next action. The Evidence line gives the command output or the Ghidra reference that shows the state of the last batch.

## Consequences

- "End of a batch" in `AGENTS.md` and `docs/WORKFLOW.md` names the Evidence line.
- A session reads open work with `gh issue list`, not from `docs/STATUS.md`. The session hook still prints the Active block, which stays short.
- The Next action names one next step and may point to issues. It is not a list of work.
