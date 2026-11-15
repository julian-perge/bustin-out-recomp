# Intent: repo overhaul

The user confirmed this statement on 2026-11-14 at the end of an interview. It is the input for
the overhaul spec. It says what the user wants. It does not say how to build it.

## Statement

- Outcome: a public GitHub decomp project that runs on the `/agent-skills` workflow.
  - `AGENTS.md` is the one instruction file, and `CLAUDE.md` points to it.
  - GitHub issues are the task queue, with a milestone tracker.
  - Contributor docs: CONTRIBUTING, LEGAL, METHODOLOGY, issue and PR templates.
  - Reader docs: ARCHITECTURE, CODE_MAP, SUBSYSTEMS.
- User: the maintainer and the maintainer's Claude agents now, and outside contributors who send
  matches later.
- Why now: the maintainer wants one workflow across all repos, the setup grew milestone by
  milestone, and some output had to be corrected. Token cost started the idea and is solved.
- Success:
  1. The repo is public from one fresh commit, with no copyrighted files and no paths from the
     maintainer's machine in tracked files.
  2. The `/agent-skills` stages run from issues, superpowers is out of the live flow, and M5 is
     the first work that goes through the new flow.
  3. One standards doc states four rules, and the reviewer agent and the PR template check
     against it.
- Constraint: the source tree, tools, build and checks do not move. `docs/FINDINGS.md` and its
  IDs keep their shape. Adding the git remote and the first push wait for the maintainer's OK.
- Out of scope: setup that works on another machine (a later milestone), Codex support,
  splitting FINDINGS into topic files, governance docs, and any M5 matching work.

## The four rules for the standards doc

1. Plausible source: code that compiles to the right bytes but that no programmer wrote in 2003
   is not a match. Nothing the compiler generates is written by hand.
2. Evidence for claims: a match, a cause or a finished task is reported with the command output
   or the Ghidra reference that proves it.
3. Evidence for names: a function, class or field name comes from a string, a symbol or the
   GameCube donor, not from a guess.
4. Stay in the task: no work past what was asked, no redoing a settled finding, no changes to
   files outside the task.

## Assumptions the user accepted

- The m0 to m4 result files stay as history.
- The M5 design that was in progress on 2026-11-14 feeds the first agent-skills spec.
- The old 147-commit history stays in a local backup.
- Contributors do not need an AI agent.

## Interview answers

- Model repos: `slaterain/nv-rs` gives the entry files (short `AGENTS.md`, pointer `CLAUDE.md`,
  a tracker that ends each batch with evidence, blockers and one next action) and the
  contributor docs. `KraftMacAndChee/Mercenaries-Recompiled` gives the reader docs. The nv-rs
  layout of one topic file per subject is not wanted.
- In scope: agent instructions and the project docs layout. Not in scope: the source tree
  layout, build and checks.
- Codex: the uncommitted `.codex/` folder is deleted. Claude Code is the only configured tool.
- History: the public repo starts from one fresh commit.
- A stranger who matches a function on their own machine is not part of "finished".

## Decisions after the statement

The user made these on 2026-11-14, after the statement. They replace the earlier assumption that
`docs/superpowers` stays as history. All of them are carried out and not committed.

- The seven finished superpowers plans are removed from the tree.
- The method design becomes `docs/METHODOLOGY.md`. The agent-workflow design is removed, and the
  rules that only it stated are in ADR-0014.
- The open work in the recall summary, the M5 thunk-trial design, is GitHub issue #1 with the
  design so far as a comment. `.recall/` is gitignored and stays on the maintainer's machine.
- Tracked files name no user home directory. `.mcp.json` uses `${HOME}`, the default XDK archive
  path in `bodecomp/setup_xdk.py` is relative to the repo, and `tests/test_machine_paths.py`
  fails when such a path returns.

## Facts found on 2026-11-14

- The GitHub repo `julian-perge/bustin-out-recomp` exists, is public and is empty. The local
  repo has it as the remote `origin`. Nothing is pushed.
- Git tracks no disc image, archive, XDK file, Ghidra project or build output, now or in the
  history. `.gitignore` covers them.
- `bodecomp.findings check` verifies that the commit of each `fixed (<commit>)` entry exists.
  `docs/FINDINGS.md` has 14 such entries. A repo that starts from one fresh commit holds none of
  those commits, so the check fails there. The spec must settle this.
- `docs/METHODOLOGY.md` still describes parts of the 2026-10-10 design that the repo did not
  adopt. Its first section lists them. The contributor docs must bring it up to date.
- `bodecomp/agent_tools.py` and `tools/ghidra-mcp-headless.sh` expect the ghidra-mcp checkout at
  `~/git/bethington/ghidra-mcp`, and five scripts in `tools/` default to the Homebrew path of
  Ghidra 12.1.4. These defaults belong to the later setup milestone.
- `AGENTS.md` and `docs/METHODOLOGY.md` send toolchain problems to `~/.config/papercuts.md`, a
  file on the maintainer's machine. The agent file rewrite must replace that rule.
- The milestone table in `docs/STATUS.md` and `docs/METHODOLOGY.md` defines M5 as the recomp
  harness. The user chose to start M5 with the thunk trial of issue #1. The milestone tracker
  must settle the numbering.
- Untracked and still on disk: `.codex/` (to delete) and `.superpowers/` (gitignored scratch).
- `/setup-agent-skills-workflow` ran on 2026-11-14. It wrote the `Every task` and `Workflow`
  blocks in `AGENTS.md`, `docs/agents/`, four labels and the `tasks/` line in `.gitignore`.
  `AGENTS.md` is the agent entry file and `CLAUDE.md` imports it (ADR-0015). Issue #1 carries
  `ready-for-human`. The other docs in the statement need their own tasks.
- The Build stage opens a pull request, and that needs a push. Nothing is pushed, and the first
  push must be the one fresh commit. No Build stage can finish before the repo is published.
