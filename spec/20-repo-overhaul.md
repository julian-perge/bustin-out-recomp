Source issue: [#20 Finish the repo overhaul: standards, contributor and reader docs, milestones](https://github.com/julian-perge/bustin-out-recomp/issues/20)

# Spec: Repo overhaul, V1

Status: approved on 2026-11-17. Open questions 2 and 3 take their proposals. Open question 1 is settled in the plan.

Commands, repo structure and code style are in [AGENTS.md](../AGENTS.md). This spec adds only what the overhaul needs.

## Objective

The repo is a public decomp project that runs on the `/agent-skills` workflow. The confirmed intent is in [docs/intent/repo-overhaul.md](../docs/intent/repo-overhaul.md).

Users: the maintainer and the maintainer's Claude agents now, and outside contributors who send matches later. A contributor does not need an AI agent.

Two of the intent's three success criteria are already met (checked 2026-11-15):

1. The repo is public from one fresh commit, 610a318, which has no parent (`git rev-list --max-parents=0 HEAD`, ADR-0016). `tests/test_machine_paths.py` fails when a tracked file names a user home directory.
2. The M5 thunk trial ran through the stages: issue #1, its spec `spec/1-virtual-base-thunk-trial.md`, and sub-issues #2 to #10, merged in pull requests #11 to #19. `superpowers` occurs only in `docs/adr/` and `docs/intent/`.

This spec covers the rest: the standards doc (criterion 3), the contributor docs, the reader docs, the milestone tracker, the move of the backlog to issues, and the rules that still name a file on the maintainer's machine.

## Decisions (maintainer, 2026-11-15)

| Question | Decision |
| --- | --- |
| Subject of the reader docs | The repo's tooling only: `bodecomp/`, `tools/`, `.claude/`, and how `src/` is laid out. Not the game's engine. |
| Milestone numbering | A new M5 holds issue #1 and the next matching work. The harness becomes M6 and the layout M7. |
| Backlog in `docs/STATUS.md` | Each item becomes a GitHub issue labeled `needs-triage`, in the right milestone. |
| `LEGAL.md` | Not in this spec. |
| Source issue | #20. |
| Doc layout | Root: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`. `docs/`: `METHODOLOGY.md`, `ARCHITECTURE.md`, `CODE_MAP.md`, `SUBSYSTEMS.md`. |
| Papercuts rule | A toolchain problem that costs time becomes a GitHub issue labeled `needs-triage`. |
| Issue forms | Task, Tool bug and Match claim. Blank issues stay allowed. |

## Requirements

### R1. `CODING_STANDARDS.md` states four rules

The file is at the root, because `docs/agents/workflow.md` already names it as the standard file of the review command. Each rule has a stable ID, a heading, the rule, what it means in this repo, and how a reviewer checks it. The rules are the four of the intent:

- `S1` Plausible source. Code that compiles to the right bytes but that no programmer wrote in 2003 is not a match. Nothing the compiler generates is written by hand (ADR-0013).
- `S2` Evidence for claims. A match, a cause or a finished task is reported with the command output or the Ghidra reference that proves it.
- `S3` Evidence for names. A function, class or field name comes from a string, a symbol or the GameCube donor, not from a guess (the tiers of ADR-0002, ADR-0008 and ADR-0011).
- `S4` Stay in the task. No work past what was asked, no redoing a settled finding, and no changes to files outside the task.

The rules link the ADRs and findings that apply. They do not repeat tool procedures, which stay in `docs/WORKFLOW.md`.

### R2. The reviewer agent and the PR template check against R1

- `.claude/agents/reviewer.md` reads `CODING_STANDARDS.md` before it checks. Its final report gives a pass or fail per rule, `S1` to `S4`, each failure with its evidence. Its present checks stay, each under the rule it serves. `S4` is new: the reviewer compares the changed files with the task's acceptance criteria.
- `.github/pull_request_template.md` has these sections: Task (`Closes #<n>`), Change, one section per rule `S1` to `S4`, Verification (the output of the `Every task` command of `AGENTS.md`), Proposed findings (the `F-NEW` form of the reviewer agent) and Handoff (blockers and one next action).

### R3. Contributor docs

- `CONTRIBUTING.md` at the root says, in this order: what the project is and what counts as a match; what a contributor needs (their own copy of `default.xbe` and of the XDK 5558 archive); that setup on another machine is not documented yet and is a later milestone; how to find and claim work (labels, the issue forms, the Match claim form); branches, commits and pull requests (from `docs/agents/workflow.md`); the verify command; the standards doc; how a contributor proposes a finding (only the lead session edits `docs/FINDINGS.md` and `docs/STATUS.md`); and how the maintainer merges (a merge commit when a pull request's findings cite its own commits, ADR-0016).
- `docs/METHODOLOGY.md` describes the repo as it is at the commit that changes it:
  - The first section, which lists the parts of the 2026-10-10 design that the repo did not adopt, is removed. Each of those parts is rewritten to what the repo does: the build is `bodecomp.match` and `docs/LEDGER.md`, the batch logs are the `docs/m*-results.md` files and `docs/thunk-trial-results.md`, and functions are named when they are matched (ADR-0009, ADR-0011, F-0029).
  - The working rule about `~/.config/papercuts.md` is replaced by the rule of R6.
  - "Phase 1: the agent workflow" links `docs/agents/workflow.md` for the stages.
  - The milestone table has the numbers of R4.
  - The table "Decisions made at the start" stays as the record of 2026-10-10. A row that a later ADR changed names that ADR.
- `.github/ISSUE_TEMPLATE/` holds three forms. Each form sets the label `needs-triage`.
  - `task.yml`: Parent (optional), Spec (optional), What to build, Acceptance criteria, Verification. The fields are the task body of `docs/agents/workflow.md`.
  - `tool-bug.yml`: the command, its output, the expected result, the commit.
  - `match-claim.yml`: the addresses or the class, the planned source file, and the GameCube donor's name when there is one. The maintainer assigns the claimant at triage.

### R4. Milestone tracker

- GitHub milestones exist for M0 to M7. M0 to M4 are closed. Each description gives the exit condition and links the milestone's results file.
- M5 is the new matching milestone. Issues #1 to #10 are in it. The harness is M6 and the layout is M7.
- The milestone tables in `docs/STATUS.md` and `docs/METHODOLOGY.md` have the same rows, with the new numbers.
- ADR-0018 records the renumbering and that GitHub milestones group the issues, while the table in `docs/STATUS.md` stays the record of each exit condition and result.

### R5. The backlog moves to issues, and the Active block ends with evidence

- Each item on the Backlog line of the Active block becomes one issue labeled `needs-triage`. Its body holds the item's text, the finding IDs it cites, and the commit of `docs/STATUS.md` it came from. The plan lists each item with its proposed issue title and milestone, and the maintainer approves the list before any issue is opened.
- The Active block loses its Backlog line and gains an Evidence line: the command output or the Ghidra reference that shows the state of the last batch. Its fields are Branch, Running, Owners, Evidence, Blockers and Next action.
- "End of a batch" in `AGENTS.md` names the Evidence line.
- ADR-0019 records that GitHub issues are the only task queue and that `docs/STATUS.md` holds no backlog.

### R6. Agent instructions name nothing on the maintainer's machine

- `AGENTS.md` and `docs/METHODOLOGY.md` replace the papercuts rule with: a toolchain problem that costs time becomes a GitHub issue labeled `needs-triage`, with the symptom, the cause (evidence or guess) and the fix.
- "Where things live" in `AGENTS.md` links `CONTRIBUTING.md`, `CODING_STANDARDS.md` and the three reader docs. `AGENTS.md` stays at or under 100 lines (ADR-0014).
- "Working on it" in `README.md` links `CONTRIBUTING.md`.

### R7. Reader docs about the tooling

Each file starts with the commit and the date at which its claims were checked against the repo. Each claim about a file or a command is true at that commit.

- `docs/ARCHITECTURE.md`: the central design (text in git is the source of truth and Ghidra is rebuilt from it, ADR-0002), the data flow from the inputs to the ledger (inputs and setup, Ghidra rebuild and sync, delink into per-unit objects, the re-link gate, matching with VC71 under wibo, the ledger and the README block), the agent roles and the one-writer rule (ADR-0003), and the boundaries: what stays out of git and what is out of scope (the recomp harness is M6).
- `docs/CODE_MAP.md`: a table that starts with the question ("Why is this function not `matched`?", "Where does a name come from?") and gives the file to start in and the files to follow; the role of each top-level directory; the entry points (the commands of `AGENTS.md`); and the tests to run for each area.
- `docs/SUBSYSTEMS.md`: one section per tool subsystem, each with its purpose, its input and output files, its commands, its tests, and the ADRs and findings that apply. The subsystems are: inputs and setup; the Ghidra rebuild and name sync; delink and re-link; SDK names from the XDK libraries; matching; the trivial-function generator; code outside functions; string names; the ledger, the README block and the findings check; and the agents and the session hook. Every module in `bodecomp/` and every script in `tools/` is named in exactly one section.

## Tech stack

No change. Python 3 with `uv`, pytest and ruff; bash scripts in `tools/`; the `gh` CLI for issues and milestones.

## Commands

The `Every task` command of `AGENTS.md` runs before each commit. The overhaul adds:

```
Doc checks:  uv run pytest -q tests/test_docs.py
Milestones:  gh api 'repos/julian-perge/bustin-out-recomp/milestones?state=all' --jq '.[] | [.title,.state,.open_issues,.closed_issues] | @tsv'
Triage list: gh issue list --repo julian-perge/bustin-out-recomp --label needs-triage --state open --json number,title,milestone
Stale words: rg -n 'configure\.py|ninja|docs/batches|papercuts\.md|superpowers' docs/METHODOLOGY.md AGENTS.md
```

## Project structure

New files:

```
CONTRIBUTING.md                         How to contribute (R3)
CODING_STANDARDS.md                     The four rules S1 to S4 (R1)
.github/pull_request_template.md        One section per rule (R2)
.github/ISSUE_TEMPLATE/task.yml         Task form (R3)
.github/ISSUE_TEMPLATE/tool-bug.yml     Tool bug form (R3)
.github/ISSUE_TEMPLATE/match-claim.yml  Match claim form (R3)
docs/ARCHITECTURE.md                    Design and data flow of the tooling (R7)
docs/CODE_MAP.md                        Question to file (R7)
docs/SUBSYSTEMS.md                      One section per tool subsystem (R7)
docs/adr/0018-*.md, docs/adr/0019-*.md  Decisions of R4 and R5
tests/test_docs.py                      Checks of the testing strategy
```

Changed files: `AGENTS.md`, `README.md`, `docs/METHODOLOGY.md`, `docs/STATUS.md`, `docs/adr/README.md`, `.claude/agents/reviewer.md`.

## Code style

Docs follow the rules of `AGENTS.md`: ASCII only, short sentences, one idea per sentence, the active voice, and a causal claim says whether it rests on evidence or is a guess. A rule in `CODING_STANDARDS.md` looks like this:

```markdown
## S3 Evidence for names

A function, class or field name comes from a string, a symbol or the GameCube donor, not from a guess.

- In this repo: each name in `config/symbols.txt` has a tier and evidence (ADR-0002).
  A `gc` name needs two independent kinds of evidence.
- The reviewer checks: the tier and the evidence of each new name, through ghidra-mcp.
```

A row of `docs/CODE_MAP.md` looks like this:

```markdown
| Why is a function not `matched`? | `bodecomp/match.py` | `config/functions.csv`, the unit in `build/target`, `docs/WORKFLOW.md` "Matching" |
```

## Testing strategy

`tests/test_docs.py` runs in `uv run pytest -q` and reads only tracked files. It fails when:

1. A rule ID in `CODING_STANDARDS.md` is missing from `.claude/agents/reviewer.md` or `.github/pull_request_template.md`.
2. An issue form in `.github/ISSUE_TEMPLATE/` does not set the label `needs-triage`. The test reads the text; the repo has no YAML dependency.
3. A relative Markdown link in `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `docs/METHODOLOGY.md` or a reader doc points to a path that git does not track.
4. A module in `bodecomp/` (other than `__init__.py`) or a script in `tools/` is not named in `docs/SUBSYSTEMS.md`.
5. The milestone rows of `docs/STATUS.md` and `docs/METHODOLOGY.md` differ in number or name.
6. `AGENTS.md` has more than 100 lines, or a tracked `.md` file holds a character that is not ASCII. All tracked `.md` files were ASCII on 2026-11-15.

GitHub state (milestones, issues, labels) has no test. Each task that changes it gives the `gh` command and its output in its pull request (S2).

## Boundaries

- Always: check each fact in a doc against the repo, `gh` or Ghidra at the commit that writes it, and give the command or reference (S2). Keep `AGENTS.md` at or under 100 lines. Keep docs ASCII.
- Ask first: every GitHub write that the plan does not list (milestones, issues, labels, closing an issue). Opening the backlog issues: the maintainer approves the list first. A change to an existing ADR other than its status line.
- Never: move or change the source tree, `bodecomp/`, `tools/`, the build or the existing checks. Change the shape or the IDs of `docs/FINDINGS.md`. Remove the `docs/m*-results.md` files. Write `LEGAL.md`, setup docs for another machine, or Codex config. Do matching work.

## Success criteria

1. `CODING_STANDARDS.md` states `S1` to `S4` with the text of R1, and `uv run pytest -q tests/test_docs.py` passes.
2. The reviewer's final report form in `.claude/agents/reviewer.md` has a pass or fail per rule, and the PR template has one section per rule (checked by test 1).
3. `CONTRIBUTING.md` and the three issue forms exist. After the merge, `gh api repos/julian-perge/bustin-out-recomp/community/profile --jq '.files.contributing.url, .files.pull_request_template.url'` prints two URLs.
4. The stale-words command of "Commands" prints nothing.
5. The three reader docs exist in `docs/` and tests 3 and 4 pass.
6. The milestones command lists M0 to M7, with M0 to M4 closed and issues #1 to #10 in M5. ADR-0018 is in `docs/adr/` and in its index.
7. The Active block of `docs/STATUS.md` has no Backlog line and has an Evidence line. Every item of the backlog at the commit before the change has an issue, and the pull request lists each item with its issue number. ADR-0019 is in `docs/adr/` and in its index. `tests/test_session_start.py` passes, so the hook still prints at most 40 lines.
8. `git diff --name-only <base>..HEAD -- src bodecomp tools config` prints nothing, where `<base>` is the commit `main` was at when the work started.
9. The `Every task` command of `AGENTS.md` passes, and `bodecomp.match --check` reports the same matched count as at `<base>` (3363 on 2026-11-15).

## Out of scope (deferred)

- `LEGAL.md`: the maintainer's choice of 2026-11-15.
- Setup on another machine: a later milestone. It holds the paths of ghidra-mcp and Ghidra in `tools/` and `bodecomp/agent_tools.py`, the Homebrew path in `.mcp.json`, a `.gitattributes` file, and the builds of ghidra-xbe and ghidra-mcp.
- Docs about the game's engine subsystems: they wait until more functions are named.
- A check that finds drift in the reader docs past links and module names.
- Turning off blank issues, and CI on GitHub Actions: not asked for.
- Codex support, splitting `docs/FINDINGS.md` into topic files, governance docs, and M5 matching work: out of scope in the intent.

## Risks

| Risk | Mitigation |
| --- | --- |
| The reader docs drift from the code | Each starts with the commit it was checked at. Tests 3 and 4 catch moved files and new modules. |
| The backlog issues lose the finding context | Each body cites its finding IDs and the commit of `docs/STATUS.md`. |
| The PR template asks more than an outside contributor can give | Each rule section asks for the evidence the rule names and nothing else. |

## Open questions

1. What is the new M5's name and exit condition? The trial's outcome sends the next work to "the search for the next byte shape among larger functions" (`docs/thunk-trial-results.md`), and that search has no issue yet.
2. Do issue #20 and its tasks belong to a milestone? The proposal is none, because the milestones measure the decomp.
3. Does the PR template ask whether an AI tool helped, as the nv-rs template does? The proposal is no, because a contributor does not need an AI agent.
