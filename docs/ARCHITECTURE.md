# Architecture of the tooling

Checked against the repo at commit 8260a0c on 2026-11-17.

This file describes how the repo's tools fit together. It does not describe the game's engine. [SUBSYSTEMS.md](SUBSYSTEMS.md) gives the detail of each part, [CODE_MAP.md](CODE_MAP.md) says where to start reading, and [WORKFLOW.md](WORKFLOW.md) gives the procedures.

## The central design

Text files in git are the source of truth, and the Ghidra project is rebuilt from them ([ADR-0002](adr/0002-text-is-the-source-of-truth.md)). `config/symbols.txt` holds every name with its tier and evidence. `config/functions.csv` holds the match status of every claimed function. The C++ in `src/` is the decomp itself. The Ghidra project in `ghidra/` is a workbench: `tools/rebuild-ghidra.sh` builds it again from `orig/default.xbe` and `config/symbols.txt`, so nothing important lives only there.

## Data flow

```
disc image ----------- bodecomp.setup_inputs ----> orig/default.xbe
XDK 5558.2 archive --- bodecomp.setup_xdk -------> tools/xdk/ (VC71, libs), tools/wibo/
                                                      |
orig/default.xbe + config/symbols.txt                 |
   -- tools/rebuild-ghidra.sh, bodecomp.sync ------> Ghidra project (ghidra/)
   <- bodecomp.sync export, bodecomp.names set ----  (names flow back to config/symbols.txt)
                                                      |
Ghidra project -- bodecomp.split, tools/delink.sh --> build/target/units/<unit>.obj
build/target/units/ -- bodecomp.relink -----------> gate: the units re-link to .text exactly
                                                      |
src/**/*.cpp -- VC71 CL.Exe under wibo --- bodecomp.match ---> config/functions.csv
config/symbols.txt + config/functions.csv
   -- bodecomp.ledger ---> docs/LEDGER.md
   -- bodecomp.readme ---> the progress block of README.md
```

1. Inputs and setup. `bodecomp.setup_inputs` extracts `default.xbe` from the user's disc image into `orig/` and checks its SHA-256. `bodecomp.setup_xdk` unpacks VC71 and the SDK libraries from the user's XDK archive into `tools/xdk/`, and installs wibo.
2. Ghidra rebuild and sync. The ghidra-xbe loader imports the XBE into a headless Ghidra project, and the ghidra-mcp server (`tools/ghidra-mcp-headless.sh`) serves it on port 8089. `bodecomp.sync` copies names between the project and `config/symbols.txt`. SDK functions get names from byte matches against the XDK libraries (`bodecomp.libmatch`, [ADR-0005](adr/0005-sdk-names-from-stamped-libraries.md)), and game functions from their strings (`bodecomp.names`).
3. Delink. `bodecomp.split` lists the units from the function starts. `tools/delink.sh` runs the ghidra-delinker scripts headless, and `bodecomp.unitsplit` cuts one COFF object per unit into `build/target/units/` ([ADR-0006](adr/0006-per-unit-objects-and-the-relink-gate.md)).
4. The re-link gate. `bodecomp.relink` links every unit at its original address. It must report 0 mismatched bytes, 0 unresolved names and 0 unit problems, which shows that the units are an exact cut of `.text`.
5. Matching. `bodecomp.match` compiles every `src/**/*.cpp` except `src/m0` with VC71 under wibo at `/O2 /G7 /arch:SSE /GX` ([ADR-0004](adr/0004-toolchain-and-default-flags.md), [ADR-0017](adr/0017-default-flags-gain-gx.md)). It pairs each function with its unit by the address comment before it, compares bytes and relocations, and writes `config/functions.csv`. `bodecomp.trivial` writes and matches the small functions in `src/game/trivial/`.
6. The ledger and the README block. `bodecomp.ledger` writes `docs/LEDGER.md` from `config/symbols.txt` and `config/functions.csv`. `bodecomp.readme` writes the progress block of `README.md`.

## Agent roles and the one-writer rule

Three agents in `.claude/agents/` do most of the work, under a lead session ([ADR-0007](adr/0007-agent-workflow.md), [ADR-0015](adr/0015-agents-md-is-the-entry-file.md)):

- `namer` names functions and data in Ghidra through ghidra-mcp, and syncs the names into `config/symbols.txt`.
- `matcher` writes C++ for a batch of functions in its own git worktree. It reads Ghidra and does not write to it.
- `reviewer` checks a batch against the rules `S1` to `S4` of [CODING_STANDARDS.md](../CODING_STANDARDS.md) and changes nothing.

Analysis questions go through ghidra-mcp, not through a raw search of the binary. Only one writer changes the Ghidra project at a time: the lead session or one `namer`, named by the assignee of the open task with the `ghidra-writer` label ([ADR-0003](adr/0003-ghidra-mcp-first-one-writer.md), [ADR-0021](adr/0021-generated-session-state-and-ghidra-freshness.md)). A session writes its `docs/FINDINGS.md` entries in its own pull request, and the review checks them ([ADR-0020](adr/0020-agent-push-and-merge-commit.md)). Only the lead session edits the milestone table in `docs/STATUS.md`. `tools/session-start.sh` prints the generated state of the work and the open findings at the start of each session.

## Boundaries

What stays out of git (`.gitignore`): the disc image and every archive (`*.iso`, `*.zip`, `*.7z`, `*.rar`), `orig/`, `tools/xdk/`, `tools/wibo/`, `build/`, `ghidra/`, `.venv/`, `.recall/` and `tasks/`. The tests never read the disc image. The tests that compile with VC71 use `tools/xdk/` and `tools/wibo/` when they are set up, and are skipped otherwise.

What is out of scope for the tooling now:

- The recomp harness, which runs rebuilt code under xboxrecomp. It is milestone M6.
- Source-file splits and the matching of `.data` and `.rdata`. They are milestone M7.
- Setup on another machine. The scripts in `tools/` have default paths for one machine, which a later milestone replaces.
