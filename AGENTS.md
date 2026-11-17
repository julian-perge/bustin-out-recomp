# The Sims Bustin' Out (Xbox) decomp

A byte-matching decompilation of the Xbox release: C++ that VC71 compiles back to the original bytes of `default.xbe`. The GameCube decomp (daftblazer/bustin-out-decomp) donates names, types and draft C++. The xboxrecomp static recompiler is only a phase 2 harness (ADR-0001). The method is in `docs/METHODOLOGY.md`.

## Start here

1. The SessionStart hook prints the Active block of `docs/STATUS.md`, the open and active findings, whether ghidra-mcp is up, and the branch. If it is missing, run `tools/session-start.sh`.
2. Before investigating any address, function or tool behavior, search for it: `rg -n '<address or keyword>' docs/FINDINGS.md docs/adr`. A confirmed, fixed or rejected entry is cited and not redone. Reopen one only with new evidence, and write that evidence into the entry.
3. Read the section of `docs/METHODOLOGY.md` for the task, and `docs/WORKFLOW.md` for tool procedures.

## Where things live

- [CONTRIBUTING.md](CONTRIBUTING.md): how to find, claim and send work. [CODING_STANDARDS.md](CODING_STANDARDS.md): the rules `S1` to `S4` that every change follows.
- `docs/STATUS.md`: milestones and the one Active block (branch, running processes, owners, blockers, backlog, next action).
- `docs/FINDINGS.md`: facts, one entry each with a status. `docs/adr/`: decisions about method.
- `docs/WORKFLOW.md`: the ghidra-mcp server, rebuild, delink, query recipes, end-of-batch steps, the GameCube watch.
- `docs/LEDGER.md`: generated per-function status. `docs/m0-results.md`, `docs/m1-results.md`, `docs/m2-results.md`, `docs/m3-results.md`: milestone evidence.
- `config/symbols.txt`: every name, with tier and evidence (ADR-0002).
- `.claude/agents/`: `namer`, `matcher`, `reviewer`.

## Working rules

- Use ghidra-mcp for questions about functions, references, strings, types and call graphs. Do not guess, and do not search the raw binary to draw conclusions; a raw search result is preliminary until Ghidra confirms it (ADR-0003).
- Text files in git are the source of truth; Ghidra is rebuilt from them (ADR-0002).
- A causal claim ("X caused Y") says whether it rests on evidence or is a guess.
- Repo documents are ASCII only.
- A toolchain problem that costs time becomes a GitHub issue labeled `needs-triage`, with the symptom, the cause (evidence or guess) and the fix.
- Git: local commits and merges to local `main` are allowed in this repo. Pushing or adding a remote needs the user's OK.

## Ownership

- One writer to the Ghidra project at a time: the lead session or one `namer`, named in the Active block.
- One owner per file or worktree. Long-running processes (the server, a delink) are listed in the Active block.
- Only the lead session edits `docs/FINDINGS.md` and `docs/STATUS.md`. Subagents put proposed entries in their final reports.

## Every task

Before each commit, run `uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check`.

## Workflow

- Tasks are tracked in GitHub Issues for julian-perge/bustin-out-recomp, with the `gh` CLI. `/agent-skills:plan` creates one sub-issue per task. `tasks/` is git-ignored scratch.
- Specs are files at `spec/<issue>-<slug>.md`, not `SPEC.md`.
- ADRs go in `docs/adr/`. Read `GLOSSARY.md` and `docs/adr/` (those that exist) before design work.
- Read `docs/agents/workflow.md` before any `/agent-skills` command.

## End of a batch

1. `uv run pytest -q`
2. `uv run python -m bodecomp.ledger` and `uv run python -m bodecomp.findings check`
3. Replace the Active block of `docs/STATUS.md`; add or update FINDINGS entries.

At the end of a plan, also set unfinished `active` findings back to `open`. Record a decision as an ADR when it is settled (ADR-0014).

## Commands

- Tests: `uv run pytest -q`. Lint: `uv run ruff check .`
- Names: `uv run python -m bodecomp.sync export|apply|check`
- Matching: `uv run python -m bodecomp.match [--check]`, `uv run python -m bodecomp.match candidates N`
- Trivial functions: `uv run python -m bodecomp.trivial generate [--max-size N]`, `uv run python -m bodecomp.trivial shapes [N]`
- Ghidra server: `tools/ghidra-mcp-headless.sh`. Rebuild: `tools/rebuild-ghidra.sh`. Delink: `tools/delink.sh`. Re-link: `uv run python -m bodecomp.relink`
- Code outside functions: `uv run python -m bodecomp.gaps report|candidates|starts`, then `tools/create-functions.sh` (server stopped)
- String names: `tools/export-strings.sh` (server stopped), then `uv run python -m bodecomp.names stated|batch N|set|clear|check`. Matched names: `names set 0xADDRESS NAME src/PATH.cpp`
- Read-only tool list for the agents: `uv run python -m bodecomp.agent_tools`
- README progress block: `uv run python -m bodecomp.readme` (the user runs it occasionally; it is not part of the end of a batch)
