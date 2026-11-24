# Research: an agent session that works for a night with no person

Date: 2026-11-24. Question: what must change in this repo so that one session can be started with "work for 8 hours" and then run alone? This folder holds the sources, the facts and a design. It changes no workflow file. [01-method.md](01-method.md) gives the sources, the citation rules and the checks.

## The answer in short

1. **No source proves it.** None of the 10 repos shows a session that ran for a night with no person. dx-ball, the nearest, had at least six actions of a person, and one of them ended a block of 94.8 hours. zx-reaper's own report says that its agents stalled overnight until the author came back. The only proven unattended runs are benchmark runs of 30 minutes at most (rea-lab).
2. **The loop exists in Claude Code.** `/goal` keeps one session working until a condition holds, waits for a usage limit, and returns after a resume. Its judge reads only the conversation, so the clock must be a command whose output the session prints.
3. **This repo has the hard part.** Each working project has a check against the original that a program runs. This repo has it (`bodecomp.match`), with a ledger that only the check writes and a queue that a command computes.
4. **This repo lacks five things:** a rule that lets a session run batch after batch, a clock, permissions with no prompts, a place for questions when nobody answers, and a check before the run. [10-overnight-design.md](10-overnight-design.md) gives ten recommendations (R1 to R10) for them, each with the file that changes.
5. **Two settings in the working tree do nothing.** `"defaultMode": "auto"` has no effect in a project settings file, and the `sandbox` block has no `enabled` key ([09-claude-code.md](09-claude-code.md), section 1).
6. **Auto mode lets a push to `main` pass.** The night needs a deny rule and, for certainty, branch protection on GitHub (R5).
7. **REA is not needed.** It has no lane for an XBE loader and no tools that write types. Five studies with 482 runs found no gain in solve rate for Claude Code and about twice the cost ([08-lists-and-experiments.md](08-lists-and-experiments.md)).

## Files

| File | Content |
| --- | --- |
| [01-method.md](01-method.md) | Sources with commit hashes, tools used, citation rules, checks, limits |
| [02-video.md](02-video.md) | The video: 31 claims with time stamps, each checked against the clones |
| [03-dx-ball.md](03-dx-ball.md) | The deep dive: instructions, REA and Ghidra setup, loop, gates, ledgers, the six human actions |
| [04-rea-and-bun.md](04-rea-and-bun.md) | What REA is and ships, how it drives Ghidra, and the setup of `rea-agents` with bun |
| [05-baocut.md](05-baocut.md) | A video editor, not a reverse engineering project. Its watchdog design |
| [06-open-scrantic-hexgrab.md](06-open-scrantic-hexgrab.md) | A gate that passes with no data, and a scorecard method |
| [07-a6000.md](07-a6000.md) | State files, task files for delegated runs, a hot analysis daemon |
| [08-lists-and-experiments.md](08-lists-and-experiments.md) | The community list, the copy of it, the five rea-lab studies and their harness |
| [09-claude-code.md](09-claude-code.md) | The Claude Code facts that an unattended run depends on, with quotes from the documentation |
| [10-overnight-design.md](10-overnight-design.md) | The design: R1 to R10, two open decisions, the order of work, what can still stop a night |
| [11-overnight-prompt.md](11-overnight-prompt.md) | Two drafts of the prompt: one for after the design is built, one for the repo as it is |
| [12-zx-reaper.md](12-zx-reaper.md) | A harness for byte-exact rebuilds, and its overnight stall |

## What the sources agree on

| Point | Sources |
| --- | --- |
| The check against the original does the work, not the agent | Video [04:30]; dx-ball's compare command (03, section 5); zx-reaper's `make` (12, section 3); rea-lab's oracle (08, section 3) |
| A gate that the agent is only told to run, or that passes with no data, fails without notice | open-scrantic (06); a6000 CI skips (07, section 5); zx-reaper (12, section 3); the awesome list's validator (08, section 2) |
| State must be in files that a new context reads first | dx-ball handoff (03, section 7); a6000 `knowledge/CURRENT.md` (07, section 6); zx-reaper (12, section 4); Anthropic's post (09, section 8) |
| Free-text state grows until it is too long to read | dx-ball's handoff of 1,430 lines (03); a6000's brief that tells agents not to read the state files whole (07, section 8) |
| An agent with nobody to ask must be told so | rea-lab (08, section 4); a6000 briefs (07, section 2) |
| Long runs stall, and a person restarts them | dx-ball (03, section 7); zx-reaper (12, section 4) |

## The design in one table

| | Recommendation | Main file |
| --- | --- | --- |
| R1 | ADR-0023 "An unattended run", and one sentence in the stage rules | `docs/adr/0023-unattended-run.md`, `docs/agents/workflow.md`, `docs/WORKFLOW.md` |
| R2 | A clock and progress command with a stall line | `bodecomp/overnight.py` |
| R3 | Run state in three files, one of them free text | `build/overnight/` |
| R4 | A pre-flight check that fails on a stale Ghidra project, missing inputs or a red gate | `bodecomp/overnight.py` |
| R5 | `--permission-mode auto`, and a settings file for the night with allow and deny rules | `config/overnight-settings.json`, `.claude/settings.json` |
| R6 | The batch loop on one run branch with one pull request | `docs/WORKFLOW.md` |
| R7 | No question stops the run: `GUESS:` and `USER:` lines | `docs/WORKFLOW.md` |
| R8 | Five additions to the matcher's instructions | `.claude/agents/matcher.md` |
| R9 | One line from the session hook when a run is live | `tools/session-start.sh` |
| R10 | Rehearsals of 1 hour before the first night | none |

## Open decisions

**D1. Who merges the pull request of a night.** `docs/agents/workflow.md` says that the user merges. The user's global instructions say that an unattended run merges when the merge gate passes. Options: (a) the user merges in the morning; (b) the run merges after its own gate passes. Recommendation: (a) for the first nights, because the repo has no CI workflow and the only review in the night is a Sonnet subagent. Next action: the user chooses, and ADR-0023 records it.

**D2. The Bash sandbox.** Options: (a) off; (b) on, after a test that VC71 under `wibo`, `uv`, `gh` and the ghidra-mcp bridge work inside it. Recommendation: (a) now, with one `needs-triage` issue for the test. Next action: none until that test is done.

## Verification

The last run of the three citation checks over this folder (2026-11-24):

| Check | Citations | Passed |
| --- | ---: | ---: |
| A quote is on the cited line of the clone or of this repo | 449 | 449 |
| A quote is in the fetched documentation page | 60 | 60 |
| A quote is in the video transcript at the stamp | 34 | 34 |

Not covered by a script: the lines in Chinese that are cited by path and line with a translation, the numbers marked "Computed", and each claim marked UNVERIFIED. Four of the "Computed" numbers of 03 were computed a second time and agree.

The repo gate passed on this branch before the commit: `uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check`.
