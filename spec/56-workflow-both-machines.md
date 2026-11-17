Source issue: [#56 Run the agent-skills workflow on the current layout, on both machines](https://github.com/julian-perge/bustin-out-recomp/issues/56)

# Spec: agent-skills workflow on the current layout, on both machines, V1

Status: approved by the maintainer on 2026-11-17.

Commands, repo structure and code style are in [AGENTS.md](../AGENTS.md). This spec adds only what the change needs. The direction comes from the idea comment on #56 (2026-11-17). The decisions in the next table are the maintainer's answers of 2026-11-17.

## Objective

Each `/agent-skills` stage session runs on the current plugin contract (0.9.1 in the plugin cache of the maintainer's WSL machine) on the Mac and in WSL. A session asks only about real choices. No decision and no state lives on one machine only.

Users: the maintainer and the maintainer's Claude sessions. A contributor without an agent is not affected.

## Decisions (maintainer, 2026-11-17)

| Question | Decision |
| --- | --- |
| Parts | One spec, three parts: layout and rules, generated Active block, Ghidra freshness. |
| Ghidra writer in the generated block | A `ghidra-writer` label on the task issue. The assignee is the lock. |
| Ghidra state not in a text file | A writer task may change only what a tracked text file records. Other changes in Ghidra are scratch and lost on a rebuild (ADR-0002). |
| Replacement for the Evidence line | The Verification section of the pull request. The hook prints the last merged pull request only. |
| `.mcp.json` | Untracked and git-ignored. Each machine keeps its own copy. Applied in the working tree with the spec. |
| Same F-number in two pull requests | `findings check` fails on a duplicate ID. The pull request that merges second renumbers its entries before the merge. |

## Current behavior

- `docs/agents/workflow.md` and the `## Workflow` block of `AGENTS.md` have the layout from before the `agent-skills brief`, `decide`, `ac` and `next-cmd` verbs.
- `AGENTS.md` says every push needs the user's OK. Eight of 16 questions in the build and review sessions of #2 to #7 asked for it.
- `docs/STATUS.md` holds a hand-written Active block. Each merge needs a follow-up commit. `tools/session-start.sh` prints the block. `.claude/agents/namer.md` and `reviewer.md` read the Ghidra writer from it, and `matcher.md` reads the block.
- ADR-0016 asks for a merge commit only for a pull request whose findings cite its own commits. The squash merge of #11 broke `findings check` on GitHub.
- Only the lead session edits `docs/FINDINGS.md` and `docs/STATUS.md` (`AGENTS.md` Ownership, `CODING_STANDARDS.md` S4, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `.github/pull_request_template.md`).
- `tools/delink.sh`, `ghidra-mcp-headless.sh`, `rebuild-ghidra.sh` and `export-strings.sh` default `GHIDRA_HOME` to the Mac path `/opt/homebrew/Cellar/ghidra/12.2/libexec`. `.mcp.json` starts the bridge with `/opt/homebrew/bin/uv`. Evidence: `rg -n 'homebrew' tools .mcp.json`. A Ghidra-writer task in WSL needs an override for each of them.
- `bodecomp.sync check` compares `config/symbols.txt` with the open project. Nothing records that a project is level with `HEAD`.

## Requirements

### R1. Current layout and rules

1. Run `/agent-skills:setup-workflow`. It updates `docs/agents/workflow.md`, `docs/agents/issue-tracker.md` and the `## Workflow` block of `AGENTS.md`. The repo's own rules (items 2 to 5) must survive the run: compare the diff before and after.
2. `AGENTS.md` Git rule: an agent pushes a feature branch and opens a pull request without asking. A push to `main` and adding a remote still need the user's OK.
3. `docs/agents/workflow.md`, Review: every pull request merges with a merge commit, never squash or rebase. This replaces the conditional sentence of ADR-0016 and of `CONTRIBUTING.md` ("How the maintainer merges").
4. `docs/agents/workflow.md`, Spec: the pull request of a spec merges before the Plan stage, because task branches start from `main`.
5. A stage session writes its `docs/FINDINGS.md` entries in its own pull request. The review checks them. These files lose the lead-only rule for findings: `AGENTS.md` Ownership, `CODING_STANDARDS.md` S4, `CONTRIBUTING.md` (Propose a finding), `docs/ARCHITECTURE.md`, `.github/pull_request_template.md` (Proposed findings section). The `namer`, `matcher` and `reviewer` agents still do not edit it; they put proposed entries in their reports.
6. `bodecomp.findings check` fails on a duplicate finding ID and names both entries. `CONTRIBUTING.md` and the pull request template say: the pull request that merges second renumbers its entries.
7. ADR-0020 records items 2 to 6. It amends ADR-0016 and cites the incident of #11.

### R2. A generated Active block

1. `docs/STATUS.md` keeps the intro and the milestone table. It loses the Active block and its markers. The old block stays in git history.
2. `tools/session-start.sh` prints a generated block. It has these lines, each with one source:

   | Line | Source |
   | --- | --- |
   | Branch and uncommitted count | `git` on this machine |
   | ghidra-mcp up or down | `curl` to port 8089, as now |
   | Running processes | `pgrep` for the ghidra-mcp server, `analyzeHeadless` and the delinker, on this machine |
   | Ghidra writer | `gh issue list --label ghidra-writer --state open --assignee '*'`: number, title, assignee |
   | Open pull requests | `gh pr list` |
   | Assigned open issues | `gh issue list --assignee @me` |
   | Next command | `agent-skills next` |
   | Last merged pull request | `gh pr list --state merged --limit 1`: number, title |
   | Open and active findings | `bodecomp.findings summary`, as now |

3. The hook stays under 40 lines and exits 0. When `gh` or `agent-skills` is missing, offline or not signed in, the hook prints one line per missing source and goes on.
4. The `ghidra-writer` label exists on GitHub. The Plan stage puts it on each task that changes the Ghidra project. At most one open task with the label is assigned at a time; the hook prints a warning when two are.
5. `namer.md` replaces its first step (`rg 'Ghidra writer' docs/STATUS.md`) with the `gh` query above. It stops when an open task with the label is assigned to someone else. `reviewer.md` replaces its step 2 the same way. `matcher.md` step 1 (read the Active block) becomes "read the hook output".
6. "End of a batch" in `AGENTS.md` and `docs/WORKFLOW.md` loses step 3 (replace the Active block). The Evidence goes in the Verification section of the pull request. `docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, `docs/SUBSYSTEMS.md` and `AGENTS.md` (Start here, Where things live, Ownership) name the generated block instead of the file.
7. ADR-0021 records R2 and R3. It amends ADR-0003 (the writer is named by a label), ADR-0007 (the hook) and ADR-0019 (the fields of the Active block).

### R3. Ghidra project freshness on each machine

1. `bodecomp.sync check` writes the git-ignored file `ghidra/.sync-stamp` when it ends with 0 differences both ways. The file holds two hashes: the SHA-256 of `config/symbols.txt`, and the SHA-256 of its `function` lines. No other command writes it.
2. `tools/session-start.sh` compares the stamp with the current `config/symbols.txt` and prints one line:
   - Level: `ghidra project: level with config/symbols.txt`.
   - No stamp: `ghidra project: no sync stamp, run tools/rebuild-ghidra.sh, then sync apply and sync check`.
   - The `function` lines differ: the rebuild command above (`sync apply` does not create functions).
   - Only other lines differ: `run sync apply and sync check`.
3. The hook does not need the server. It reads files only.
4. Each of the four scripts that run Ghidra finds it on both machines without a manual override: Mac with Homebrew, WSL with Linuxbrew. `GHIDRA_HOME` stays as an override. One shared file sets the default. `.mcp.json` is untracked and git-ignored (maintainer decision, 2026-11-17), so each machine keeps its own copy with its own path to `uv`. `docs/WORKFLOW.md` says that the file is per machine and gives its content (the bridge command and `--no-lazy`, F-0023).
5. A Ghidra-writer task commits `config/symbols.txt` after `sync export` (as now). A change in Ghidra that no tracked text file records is scratch (decision above) and the task does not count it as done.

## Testing strategy

- `tests/test_session_start.py`: update for the generated block. Fake `gh` and `agent-skills` with scripts on `PATH`, as the file already fakes the server. Cases: all sources present; `gh` missing; two open assigned `ghidra-writer` tasks; stamp level, absent, behind on functions, behind on names.
- `tests/test_findings.py` (or the file that tests `bodecomp.findings`): a duplicate ID fails the check and names both entries.
- `tests/test_sync.py`: `check` writes the stamp on 0 differences and does not write it on a difference.
- `tests/test_docs.py`: still passes. Add a check that no tracked doc names the removed Active block markers.
- A test that no script under `tools/` names `/opt/homebrew` outside the one shared default file.
- Manual, once on each machine: run the stamp cycle (`rebuild`, `sync apply`, `sync check`), then change one name in `config/symbols.txt` and confirm the hook prints the matching step. This is the evidence for R3 on WSL and on the Mac.

## Success criteria

1. `agent-skills brief spec 56` and the stage commands run in this repo with no raw `gh` call for routine reads. A build or review session on a task issue asks no question about a push.
2. After a merge, `git status` is clean and no follow-up commit is needed. `rg -n 'active:start|active:end' .` finds nothing outside git history.
3. `tools/session-start.sh` prints the block of R2 in 40 lines or fewer, exits 0 with `gh` removed from `PATH`, and prints the stamp line of R3 on both machines.
4. After a Ghidra-writer task merges on machine A, the hook on machine B prints a behind line with the right step. After that step, the hook prints the level line.
5. `uv run pytest -q`, `uv run ruff check .`, `uv run python -m bodecomp.findings check` and `uv run python -m bodecomp.match --check` pass. `match --check` output is unchanged from `ce12545` (3363 matched, 0 nonmatching, 5 parked, 0 error).
6. `git diff --name-only 1320ff7..HEAD -- src config/functions.csv` prints nothing. No matching result changes.

## Boundaries

- Always: put each decision of R1 and R2 in an ADR (ADR-0020, ADR-0021). Keep repo documents ASCII only. Run the `Every task` command before each commit.
- Ask first: a new label other than `ghidra-writer`; a change to `.claude/settings.json` hooks other than the existing SessionStart entry; a push to `main`.
- Never: change the agent-skills plugin (bugs go to the agent-skills fork); add a stage orchestrator or a headless `claude -p` run; route tasks to a machine by label; edit `config/symbols.txt` by hand; weaken a test to make a check pass.

## Out of scope (deferred)

- Plugin changes. The two closing-keyword bugs from the idea comment go to the agent-skills fork. The agent-skills repo at `~/code/agent-skills` has a closing-keyword fix in 0.9.1 (commit 3ab37a9). I did not check that it covers both bugs.
- Machine routing labels. Either machine runs a Ghidra-writer task once R3 holds.
- A stage orchestrator or headless `claude -p` runs: print mode stopped a matcher subagent 10 minutes after the lead's last turn on 2026-11-15.
- A triage stage: the 7 triage groups of the review of #54 were real choices.
- A text file for Ghidra types and comments (widening ADR-0002).
- Moving the decisions of `tasks/plan.md` into the plan's issues: the plan of #1 kept them in a git-ignored file. I guess that the cause is in the plugin's Plan stage, so this goes to the fork. This spec's own plan puts its decisions in the sub-issue bodies.

## Assumptions and open questions

Guesses I made (each can change the plan):

1. The stamp hashes file content, not a commit as the idea comment said. A content hash is exact and also works for an uncommitted `symbols.txt`. This is a guess about what you prefer.
2. `sync check` is the only writer of the stamp because it is the only command that proves equality. Evidence: ADR-0002 and `docs/WORKFLOW.md` (rebuild steps) end with `sync check`, 0 differences.
3. `sync apply` does not create missing functions. Evidence: `tools/rebuild-ghidra.sh` creates them with `tools/create-functions.sh`. Not tested. If `apply` does create them, the "functions differ" branch of R3.2 can print the shorter step.
4. `/agent-skills:setup-workflow` may overwrite the repo's own rules in `workflow.md`. Not checked. R1.1 requires the before and after diff.
5. A `function` line is a line of `config/symbols.txt` whose second column is `function` (21734 lines today).

Open for the plan:

- One shared file for the `GHIDRA_HOME` default: a sourced `tools/env.sh`, or a `bodecomp` helper. Both work; the plan picks the smaller.
- The hook asks `gh` three times per start. If that is slow, the plan may cache for 60 seconds. Not measured.
- Other paths that differ between the Mac and WSL besides `GHIDRA_HOME` and `uv` (for example the XDK libraries or `orig/`): not checked. The manual run on WSL in the testing strategy finds them.
