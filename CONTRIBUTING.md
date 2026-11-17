# Contributing

## What the project is

This repo is a byte-matching decompilation of the Xbox release of The Sims Bustin' Out. The goal is C++ source that the original compiler, VC71 from the XDK 5558, builds back into the exact bytes of the retail `default.xbe`. The method is in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

A function counts as matched only when `uv run python -m bodecomp.match` lists it as `matched`. Its built bytes then equal the original bytes outside relocation sites, and each relocation points to the same address as in the original. The source must also be code that a programmer could have written in 2003. A source that writes code the compiler generates, or that only steers the compiler, is not a match (rule `S1` of [CODING_STANDARDS.md](CODING_STANDARDS.md)).

You do not need an AI agent to contribute. The agents in `.claude/agents/` follow the same rules as people.

## What you need

- Your own copy of the game's disc image, from which `uv run python -m bodecomp.setup_inputs --iso <image>` extracts `default.xbe` to `orig/`. The repo does not ship the game.
- Your own copy of the XDK 5558.2 archive, `xbox-sdks/2003-06 - 5558.2 - SDK.7z`, from which `uv run python -m bodecomp.setup_xdk` unpacks VC71 and the SDK libraries. The repo does not ship the XDK.
- Python with `uv`.

## Setup on another machine

The full setup (Ghidra, the XBE loader, ghidra-mcp, the delinker and wibo) is not documented for another machine yet. It is the subject of a later milestone. Until then, a contributor without that setup can still read the sources and propose changes, but cannot run every check.

## Find and claim work

- Work is tracked in [GitHub issues](https://github.com/julian-perge/bustin-out-recomp/issues). Each open issue has one label that says its state, such as `needs-triage` or `ready-for-agent`. The labels are explained in [docs/agents/workflow.md](docs/agents/workflow.md), "Labels".
- Open an issue with one of the forms: Task, Tool bug or Match claim. A blank issue is allowed too. Each form sets the label `needs-triage`.
- Before you match functions or a class, open a Match claim with the addresses or the class, the planned source file and the GameCube donor's name when there is one. The maintainer assigns the claim to you at triage, so that two people do not match the same code.

## Branches, commits and pull requests

The full rules are in [docs/agents/workflow.md](docs/agents/workflow.md).

- One task, one branch, one pull request. Name the branch `<type>/<issue>-<slug>`, for example `docs/24-methodology`.
- Write commit subjects as `<type>: <subject> (#<issue>)`, for example `docs: the thunk trial's outcome is no gain (#10)`.
- Put `(#<issue>)` in the pull request title and `Closes #<issue>` in its body. Fill in each section of the pull request template.

## The verify command

Run this before each commit. Paste its output into the Verification section of the pull request.

```
uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check
```

## The standards

[CODING_STANDARDS.md](CODING_STANDARDS.md) states four rules: `S1` plausible source, `S2` evidence for claims, `S3` evidence for names and `S4` stay in the task. The pull request template has one section per rule, and the reviewer checks each one.

## Propose a finding

[docs/FINDINGS.md](docs/FINDINGS.md) holds the facts about the binary and the tools, one entry each with a status. Only the maintainer's lead session edits `docs/FINDINGS.md` and `docs/STATUS.md`. To add or change a finding, write it in the Proposed findings section of the pull request, in the form the template gives (`## F-NEW <title>`). Search `docs/FINDINGS.md` first, because a settled finding is cited and not investigated again.

## How the maintainer merges

The maintainer reviews and merges each pull request. Every pull request merges with a merge commit, never squash or rebase, because a squash or rebase merge gives the commits of the branch new hashes and a finding can cite them ([ADR-0016](docs/adr/0016-one-fresh-public-commit.md), [ADR-0020](docs/adr/0020-agent-push-and-merge-commit.md)).
