## Task

Closes #

## Change

<!-- What this pull request changes, in one to three sentences. -->

## S1 Plausible source

<!-- For a match: confirm that the source writes nothing the compiler generates (vtable pointer stores, thunks, exception-handling frames, deleting destructors) and uses no inline assembly or #pragma tricks. Write "No source change" when nothing in src/ changed. See CODING_STANDARDS.md. -->

## S2 Evidence for claims

<!-- For each match, cause or result this pull request claims: the command output or the Ghidra reference that proves it. -->

## S3 Evidence for names

<!-- For each new or changed name in config/symbols.txt: its tier and evidence. Write "No new names" when there are none. -->

## S4 Stay in the task

<!-- Confirm that each changed file serves an acceptance criterion of the task. List work you noticed but did not do. -->

## Verification

<!-- The output of the Every task command of AGENTS.md:
uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check -->

```
```

## Proposed findings

<!-- Write each new or changed finding in docs/FINDINGS.md in this pull request, and list it here in this form, or write "None". The review checks the entries (ADR-0020).
When two pull requests use the same F-number, the pull request that merges second renumbers its entries before the merge.

## F-NEW <title>
- Status: open | confirmed | rejected
- Addresses: 0x%08X, ...
- Checked: ghidra-mcp (<date>) | test <name>
- Evidence: <what you saw, with addresses>
- Next: <for open findings> | Revisit when: <for settled ones>
-->

## Handoff

<!-- Blockers, and the one next action. -->
