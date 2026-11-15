# ADR-0015: `AGENTS.md` is the agent entry file, and `CLAUDE.md` imports it

- **Status:** Accepted (user decision)
- **Date:** 2026-11-14

## Context

ADR-0007 made `CLAUDE.md` the entry point, because Claude was the only agent family in use. The repo is now published for outside contributors (ADR-0014), who can use other agent tools. Claude Code reads `CLAUDE.md`, and several other tools read `AGENTS.md`.

## Decision

- `AGENTS.md` holds the agent instructions. It is the only file to edit.
- `CLAUDE.md` holds one line, `@AGENTS.md`, which makes Claude Code load `AGENTS.md`.
- Claude Code stays the only tool the repo configures. The role agents, the hook and the permissions are in `.claude/`.
- This supersedes one rule of ADR-0007, that `CLAUDE.md` is the entry point. The 100-line limit of ADR-0014 applies to `AGENTS.md`.

## Consequences

- `AGENTS.md` carries the `Every task` and `Workflow` blocks of the agent-skills workflow, and `docs/agents/workflow.md` holds the stages.
- A Claude Code session gets no instructions when the `@AGENTS.md` line is missing, so an edit to `CLAUDE.md` must keep it.
