# Decision records

Each decision about method or architecture gets a numbered file with Status, Date, Context, Decision and Consequences. A later decision that changes an earlier one says "Supersedes ADR-NNNN", and the earlier one's status says "Superseded by ADR-NNNN". Facts about the binary and the tools go in `docs/FINDINGS.md`, not here. Search here with `rg` before proposing a change of method.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-byte-matching-with-a-gamecube-donor.md) | A byte-matching decomp with the GameCube decomp as donor; the recomp is a phase 2 harness | Accepted |
| [0002](0002-text-is-the-source-of-truth.md) | Text files are the source of truth; Ghidra is rebuilt from them | Accepted |
| [0003](0003-ghidra-mcp-first-one-writer.md) | ghidra-mcp first for analysis, one writer at a time | Accepted |
| [0004](0004-toolchain-and-default-flags.md) | XDK 5558.2 VC71 under wibo, default `/O2 /G7 /arch:SSE` | Accepted; the default flags are amended by ADR-0017 |
| [0005](0005-sdk-names-from-stamped-libraries.md) | SDK names come from byte matches against the libraries the XBE stamps | Accepted |
| [0006](0006-per-unit-objects-and-the-relink-gate.md) | Per-unit target objects, and the re-link check as a gate | Accepted |
| [0007](0007-agent-workflow.md) | The agent workflow: entry point, status, findings, decisions, role agents | Accepted; partly superseded by ADR-0014 and ADR-0015 |
| [0008](0008-string-tier-names.md) | String-tier names are recorded in text first, with string addresses as evidence | Accepted |
| [0009](0009-names-come-from-matching-after-m2b.md) | After M2b, functions are named when they are matched, not in separate naming passes | Accepted |
| [0010](0010-subagents-run-on-sonnet-in-small-batches.md) | Namer and reviewer agents run on Sonnet, in batches of 25 functions | Accepted |
| [0011](0011-matched-tier-names.md) | A matched function takes the `matched` tier, with its source file as evidence | Accepted |
| [0012](0012-gen-trivial-claims.md) | gen_trivial reads claims from the sources and lists only unclaimed units | Accepted |
| [0013](0013-no-hand-written-compiler-code.md) | A match never hand-writes code the compiler generates, and gen_trivial shapes are reviewed before use | Accepted |
| [0014](0014-agent-skills-workflow-replaces-superpowers.md) | The repo moves to the agent-skills workflow on GitHub issues, and the superpowers documents are retired | Accepted |
| [0015](0015-agents-md-is-the-entry-file.md) | `AGENTS.md` is the agent entry file, and `CLAUDE.md` imports it | Accepted |
| [0016](0016-one-fresh-public-commit.md) | The public repo starts from one fresh commit, and `config/pre-public-commits.txt` lists the hashes of the private history | Accepted |
| [0017](0017-default-flags-gain-gx.md) | The default flags gain `/GX`, so a function with an exception-handling frame can match | Accepted |
| [0018](0018-milestones-renumbered-and-on-github.md) | M5 is "Larger functions", the harness and the layout become M6 and M7, and GitHub milestones group the issues | Accepted |
