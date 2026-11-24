# ADR-0023: An unattended run

- **Status:** Accepted (user decisions D1 and D2, 2026-11-24, issue #100)
- **Date:** 2026-11-24
- **Amends:** [ADR-0019](0019-issues-are-the-only-task-queue.md) (the queue of a run), [ADR-0021](0021-generated-session-state-and-ghidra-freshness.md) (one more hook line)

## Context

`docs/agents/workflow.md` lets a session run one stage, and the user types each stage. So the repo has no rule that lets a session go from one batch to the next while nobody is at the desk. The design in `docs/research/10-overnight-design.md` (#96) proposes one session that runs matcher batches for a set number of hours. Its recommendations R1 to R7 and R9, and the user's decisions D1 and D2, are the source of this ADR.

The second night run (#97) used a prompt and no repo support. It ran 16 batches in 153 minutes, about 9.6 minutes per batch and at most about 16. It had no permission prompt and no denial. It also had no clock that survives a compaction, no deny rules and no pre-flight check.

## Decision

1. **The mode.** An unattended run is one interactive Claude Code session in `tmux`, started with `claude --permission-mode auto --settings config/overnight-settings.json`, and driven by one `/goal` whose condition names `uv run python -m bodecomp.overnight status` and `finish`. It runs matcher batches only, one matcher at a time, and writes nothing to the Ghidra project. Its rules are in `docs/WORKFLOW.md` ("An unattended run"). It is not a stage of `docs/agents/workflow.md`, and the stage rules do not apply to it.
2. **The queue.** The run takes its functions from `match candidates`, not from GitHub issues. This is an exception to ADR-0019 for the run only.
3. **The branch exception.** The run works on one branch, `match/night-<YYYY-MM-DD>`, made from `main` by `bodecomp.overnight start`. A night has no single issue, so the branch does not follow `<type>/<issue>-<slug>` of `docs/agents/workflow.md`. Each batch merges into the run branch with a merge commit, and the run branch goes to `main` through one pull request.
4. **The draft exception.** After the first push of the run branch, the run opens its pull request as a draft. `bodecomp.overnight finish` marks it ready when the gate passes. `docs/agents/workflow.md` (Build) opens a pull request ready for review. The draft state during the night is an exception to that rule.
5. **D1: the user merges the night pull request.** The run never merges it, as `docs/agents/workflow.md` (Build) says. `config/overnight-settings.json` denies `gh pr merge`. The repo has no CI workflow, so the run's gate is its own local check, and its only review is a Sonnet subagent. When the user has merged a few nights by hand, the user can let the run merge after `finish` prints `gate: pass`. That change removes the deny rule and amends this ADR.
6. **D2: no sandbox.** The run does not use the Claude Code Bash sandbox. Whether VC71 under wibo, `uv`, `gh` and the ghidra-mcp bridge work inside it is not tested. Issue #92 holds the test, and this decision is open again when that issue has a result.
7. **State.** `bodecomp.overnight` keeps the run's clock and counts in `build/overnight/run.json` and `build/overnight/log.tsv`. The lead writes one line per batch to `build/overnight/journal.md`. `/build/` is git-ignored, so the state is per machine. When `run.json` holds a live run, the session hook prints one line about it (amends ADR-0021).

## Consequences

- `docs/WORKFLOW.md` gets the section "An unattended run". `docs/agents/workflow.md` line 5, `docs/METHODOLOGY.md` ("The merge gate") and `AGENTS.md` ("Commands") point to it.
- `AGENTS.md` ("Working rules") does not change. The run pushes a feature branch and opens a pull request, which that rule already allows. A push to `main` still needs the user's OK, and `config/overnight-settings.json` denies the two written forms of it.
- A choice that the documents do not decide does not stop the run. The lead writes it as a `GUESS:` line, and a thing that only the user can do as a `USER:` line. The user reads both in the pull request in the morning.
- The rehearsal of R10 in the design tests this ADR. Its results set the stall limit of `status`, now 30 minutes (`STALL_MINUTES` in `bodecomp/overnight.py`), and `maxTurns` of the agents. The design guessed 90 minutes for the stall limit. It is 30, because the second night run (#97) took about 9.6 minutes per batch and at most about 16.
