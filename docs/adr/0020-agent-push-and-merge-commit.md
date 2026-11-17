# ADR-0020: An agent pushes a feature branch, every pull request merges with a merge commit, and a stage session writes its own findings

- **Status:** Accepted (user decision, 2026-11-17, spec/56-workflow-both-machines.md)
- **Date:** 2026-11-17
- **Amends:** [ADR-0016](0016-one-fresh-public-commit.md)

## Context

Issue #56 moves the repo to the current agent-skills layout and removes the questions that did not need a decision.

- `AGENTS.md` said that every push needs the user's OK. Eight of 16 questions in the build and review sessions of issues #2 to #7 asked for it.
- ADR-0016 asked for a merge commit only for a pull request whose findings cite its own commits. Pull request #11 (issue #2) merged with a squash: `git cat-file -p 067ddf7` shows one parent, and the four commits of the branch are not in `main`. F-0082 and F-0083 cited commits of that branch, so `bodecomp.findings check` failed on GitHub. Both entries now cite the squash commit 067ddf7.
- Only the lead session edited `docs/FINDINGS.md`. A stage session had to put its entries in the pull request text, and a later session copied them in. Two pull requests that open at the same time can both take the next F-number.

## Decision

1. An agent pushes a feature branch and opens a pull request without asking. A push to `main` and adding a remote still need the user's OK.
2. Every pull request merges with a merge commit, never squash or rebase. This replaces the conditional rule of ADR-0016. `docs/agents/workflow.md` (Review), ADR-0016 and `CONTRIBUTING.md` ("How the maintainer merges") say so.
3. The pull request of a spec merges before the Plan stage, because task branches start from `main`. `docs/agents/workflow.md` (Spec) says so.
4. A stage session writes its `docs/FINDINGS.md` entries in its own pull request, and the review checks them. The `namer`, `matcher` and `reviewer` agents still do not edit the file. They put proposed entries in their reports. Task T2 of issue #56 edits `AGENTS.md`, `CODING_STANDARDS.md` S4, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md` and the pull request template to match.
5. `bodecomp.findings check` fails on a duplicate finding ID and names both entries. The pull request that merges second renumbers its entries before the merge. Task T2 implements the check.

## Consequences

- A session that finishes a task pushes and opens the pull request at once. A wrong push is a feature branch that the user deletes.
- The history of `main` keeps every commit of every branch, so a hash that a finding cites stays valid.
- The first-parent view of `main` still shows one merge per pull request.
- The ownership rule "only the lead session edits `docs/FINDINGS.md` and `docs/STATUS.md`" now applies to `docs/STATUS.md` alone. The rule for `docs/STATUS.md` changes in ADR-0021 (task T3 and T4 of issue #56).
