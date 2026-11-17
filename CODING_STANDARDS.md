# Coding standards

These four rules apply to every change in this repo: a match, a name, a tool change or a doc. The `reviewer` agent ([.claude/agents/reviewer.md](.claude/agents/reviewer.md)) and the pull request template ([.github/pull_request_template.md](.github/pull_request_template.md)) check each change against them by ID. Tool procedures are in [docs/WORKFLOW.md](docs/WORKFLOW.md), not here.

## S1 Plausible source

Code that compiles to the right bytes but that no programmer wrote in 2003 is not a match. Nothing the compiler generates is written by hand.

- In this repo: the source reads like C++ written for VC71, not a copy of the disassembly. It does not write vtable pointer stores, this-adjusting or vtordisp thunks, exception-handling frames, deleting destructors, or calls to base and member constructors and destructors by hand ([ADR-0013](docs/adr/0013-no-hand-written-compiler-code.md)). Inline assembly, `#pragma` tricks and code that only steers the compiler void a match. A function that matches only with such code is parked with the blocker class `source shape`. Placeholder names such as `S_00018390` are allowed ([ADR-0011](docs/adr/0011-matched-tier-names.md)).
- The reviewer checks: each matched function's source for the forms above. A new gen_trivial shape gets one reviewer pass on the generated source of one example address before `generate` uses it (ADR-0013).

## S2 Evidence for claims

A match, a cause or a finished task is reported with the command output or the Ghidra reference that proves it.

- In this repo: a match is shown by `uv run python -m bodecomp.match` output that lists the function as `matched`, and by `--check`. A claim that the compiler treats one source form differently from another is shown by compiling both forms (F-0077 in [docs/FINDINGS.md](docs/FINDINGS.md)). A fact about the binary comes from ghidra-mcp, not from a raw search of the file ([ADR-0003](docs/adr/0003-ghidra-mcp-first-one-writer.md)). A causal claim says whether it rests on evidence or is a guess. A finished task shows the output of the `Every task` command of [AGENTS.md](AGENTS.md).
- The reviewer checks: it runs the commands again in the worktree and compares the output. It reads each constant, string and vtable a match depends on from Ghidra.

## S3 Evidence for names

A function, class or field name comes from a string, a symbol or the GameCube donor, not from a guess.

- In this repo: each name in `config/symbols.txt` has a tier and evidence ([ADR-0002](docs/adr/0002-text-is-the-source-of-truth.md)). A `string` name cites the addresses of the strings its function references ([ADR-0008](docs/adr/0008-string-tier-names.md)). A `gc` name needs two independent kinds of evidence ([ADR-0001](docs/adr/0001-byte-matching-with-a-gamecube-donor.md)). A `matched` name cites its source file ([ADR-0011](docs/adr/0011-matched-tier-names.md)). A name that rests only on structure, such as a vtable slot or a call pattern, stays `auto` ([ADR-0009](docs/adr/0009-names-come-from-matching-after-m2b.md)).
- The reviewer checks: the tier and the evidence of each new name, through ghidra-mcp.

## S4 Stay in the task

No work past what was asked, no redoing a settled finding, and no changes to files outside the task.

- In this repo: a change does what its issue's acceptance criteria ask and nothing more. Work noticed on the way becomes a new issue labeled `needs-triage`. A finding that is `confirmed`, `fixed` or `rejected` in [docs/FINDINGS.md](docs/FINDINGS.md) is cited, not investigated again; it is reopened only with new evidence. A session writes its `docs/FINDINGS.md` entries in its own pull request, and the review checks them ([ADR-0020](docs/adr/0020-agent-push-and-merge-commit.md)). Only the lead session edits `docs/STATUS.md`.
- The reviewer checks: it compares the list of changed files (`git diff --name-only`) with the task's acceptance criteria, and reports each file that no criterion needs.
