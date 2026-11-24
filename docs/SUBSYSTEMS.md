# Subsystems of the tooling

Checked against the repo at commit f1114ba on 2026-11-17.

This file describes the repo's own tools: the Python package `bodecomp/`, the scripts in `tools/` and the agent setup in `.claude/`. It does not describe the game's engine. [ARCHITECTURE.md](ARCHITECTURE.md) shows how the subsystems connect, and [WORKFLOW.md](WORKFLOW.md) gives the step-by-step procedures.

Each section has a `Files` line that lists the modules and scripts it owns. Each module in `bodecomp/` and each script in `tools/` is on exactly one `Files` line, and `tests/test_docs.py` fails when one is missing or repeated. Commands run from the repo root.

## Inputs and setup

Purpose: put the game's executable and the compiler where the other tools expect them. The repo ships neither.

- Files: `bodecomp/setup_inputs.py`, `bodecomp/xdvdfs.py`, `bodecomp/xbe.py`, `bodecomp/setup_xdk.py`
- Input: the disc image, and `xbox-sdks/2003-06 - 5558.2 - SDK.7z`.
- Output: `orig/default.xbe`, checked against its SHA-256; VC71, the SDK headers and the SDK libraries in `tools/xdk/xbox/`; wibo in `tools/wibo/`.
- Commands: `uv run python -m bodecomp.setup_inputs --iso <image>`, `uv run python -m bodecomp.setup_xdk`.
- How: `xdvdfs.py` reads files from the XGD1 game partition of the image. `xbe.py` parses the XBE headers, the sections and the library stamps; most other subsystems use it. `setup_xdk.py` unpacks the archive with `7zz` and downloads the macOS build of wibo 1.2.0.
- Tests: `tests/test_setup_inputs.py`, `tests/test_xdvdfs.py` (with the synthetic image of `tests/isobuild.py`), `tests/test_xbe.py` (with `tests/xbebuild.py`), `tests/test_machine_paths.py`.
- Decisions and findings: ADR-0004 (the toolchain).

## Ghidra rebuild and name sync

Purpose: keep the Ghidra project a copy of the text files in git, so that it can be thrown away and rebuilt.

- Files: `bodecomp/symbols.py`, `bodecomp/sync.py`, `bodecomp/ghidra_api.py`, `tools/rebuild-ghidra.sh`, `tools/ghidra-mcp-headless.sh`, `tools/env.sh`
- Input: `orig/default.xbe` and `config/symbols.txt` (address, kind, size, name, tier and evidence for every name).
- Output: the Ghidra project in `ghidra/` (not in git), `config/symbols.txt` after an export, and `ghidra/.sync-stamp` after a `sync check` with 0 differences.
- Commands: `tools/ghidra-mcp-headless.sh` starts the ghidra-mcp server on port 8089. `uv run python -m bodecomp.sync export|apply|check` copies names from Ghidra to the file, from the file to Ghidra, or compares both ways. `uv run python -m bodecomp.sync freshness` reads only files and prints one line that compares `ghidra/.sync-stamp` with `config/symbols.txt`. `tools/rebuild-ghidra.sh` imports the XBE again with the server stopped, then creates every function start that `config/symbols.txt` lists.
- How: `tools/env.sh` sets `GHIDRA_HOME` for every script that runs Ghidra (`tools/delink.sh`, `tools/create-functions.sh` and `tools/export-strings.sh` too). `symbols.py` reads and writes `config/symbols.txt`; most other subsystems use it. `ghidra_api.py` sends HTTP requests to the server for `sync.py`.
- Tests: `tests/test_symbols.py`, `tests/test_sync.py`, `tests/test_env_sh.py`.
- Decisions and findings: ADR-0002 (text is the source of truth), ADR-0003 (ghidra-mcp first, one writer), F-0010, F-0020.

## Delink and re-link

Purpose: cut the original `.text` into one relocatable object per unit, and prove that the cut is exact.

- Files: `bodecomp/split.py`, `bodecomp/unitsplit.py`, `bodecomp/coffwrite.py`, `bodecomp/relink.py`, `tools/delink.sh`, `tools/ghidra_scripts/ExportTextObject.java`, `tools/ghidra_scripts/ExportDelinkTables.java`, `tools/ghidra_scripts/ExportUnits.java`
- Input: the Ghidra project, `config/symbols.txt` and `orig/default.xbe`.
- Output: `build/target/units.txt`, `build/target/text.obj`, `build/target/relocs.tsv`, `build/target/symbols.tsv`, one object per unit in `build/target/units/`, and `build/relink-report.txt`.
- Commands: `uv run python -m bodecomp.split` writes the units list from the function starts. `tools/delink.sh` (server stopped) runs `ExportTextObject.java` and `ExportDelinkTables.java` headless, then `uv run python -m bodecomp.unitsplit` cuts the units. `uv run python -m bodecomp.relink` links every unit at its original address and compares the result with `.text`. `uv run python -m bodecomp.unitsplit --compare <folder>` compares the cut with the objects that `ExportUnits.java` writes.
- How: `coffwrite.py` writes COFF objects for `unitsplit.py`.
- Tests: `tests/test_split.py`, `tests/test_unitsplit.py`, `tests/test_coffwrite.py`, `tests/test_relink.py`.
- Decisions and findings: ADR-0006 (per-unit objects and the re-link gate), F-0085 (a stale units list).

## SDK names from the XDK libraries

Purpose: name the SDK code in the XBE from byte matches against the libraries that the XBE stamps, so that it is never decompiled.

- Files: `bodecomp/arlib.py`, `bodecomp/libmatch.py`, `bodecomp/libscan.py`
- Input: `orig/default.xbe`, `tools/xdk/xbox/lib/` and `config/symbols.txt`.
- Output: `sdk` names in `config/symbols.txt`, pushed to Ghidra with `sync apply`.
- Commands: `uv run python -m bodecomp.libmatch`.
- How: `arlib.py` reads the members of a `.lib` archive. `libmatch.py` compares each function with the library functions, and skips the bytes at relocation sites. `libscan.py` finds the files that contain a byte string; only its test uses it.
- Tests: `tests/test_arlib.py`, `tests/test_libmatch.py`, `tests/test_libscan.py`.
- Decisions and findings: ADR-0005, F-0012.

## Matching

Purpose: compile the C++ in `src/` with VC71 and compare each function with its original unit.

- Files: `bodecomp/cl.py`, `bodecomp/coff.py`, `bodecomp/match.py`, `bodecomp/m0.py`
- Input: `src/**/*.cpp` (except `src/m0`), `build/target/units/`, `build/target/symbols.tsv`, `config/symbols.txt` and `orig/default.xbe`.
- Output: `config/functions.csv` (one row per claimed function: `matched`, `nonmatching`, `parked` or `error`) and the built objects in `build/match/`.
- Commands: `uv run python -m bodecomp.match [--check]`, `uv run python -m bodecomp.match candidates N`. `--check` fails when `config/functions.csv` is stale.
- How: `cl.py` runs `tools/xdk/xbox/bin/vc71/CL.Exe` under wibo. `coff.py` parses COFF objects; most subsystems use it. `match.py` pairs each function by its address comment, and reads the `declared` and `generated` lines. `m0.py` ran the flag matrix of M0 over `config/m0_candidates.csv` and `src/m0/`; `match.py` leaves `src/m0/` to it.
- Tests: `tests/test_cl.py`, `tests/test_coff.py`, `tests/test_match.py`, `tests/test_m0.py`. `tests/coffbuild.py` builds the synthetic COFF objects that these and other tests use. The tests that compile run only when `tools/wibo` and VC71 are set up.
- Decisions and findings: ADR-0004 and ADR-0017 (default flags), ADR-0011 (the `matched` tier), ADR-0013 (no hand-written compiler code), F-0086, F-0089.

## Trivial-function generator

Purpose: write and match the C++ for small game functions by their byte shape, so that a person or an agent does not write them one by one.

- Files: `bodecomp/trivial.py`
- Input: the units of 16 bytes or less, `build/strings.tsv` and the claims in `src/`.
- Output: scratch files in `build/trivial/`, the matched functions in `src/game/trivial/`, and `config/functions.csv`.
- Commands: `uv run python -m bodecomp.trivial generate [--max-size N]`, `uv run python -m bodecomp.trivial shapes [N]`.
- Tests: `tests/test_trivial.py`.
- Decisions and findings: ADR-0012 (claims), ADR-0013 (a reviewer pass for each new shape), F-0073.

## Code outside functions

Purpose: find code in `.text` that no Ghidra function covers, and create functions for it.

- Files: `bodecomp/gaps.py`, `tools/create-functions.sh`, `tools/ghidra_scripts/CreateFunctions.java`
- Input: `orig/default.xbe` and `config/symbols.txt`.
- Output: `build/target/candidates.txt`, `build/target/starts.txt`, `build/create-functions.log` and `build/create-functions-rejected.txt`.
- Commands: `uv run python -m bodecomp.gaps report|candidates|starts`, then `tools/create-functions.sh` with the server stopped. `tools/rebuild-ghidra.sh` also runs `gaps starts` and `tools/create-functions.sh`.
- Tests: `tests/test_gaps.py`, `tests/test_create_functions.py`.
- Decisions and findings: F-0016, F-0026, F-0082.

## String names

Purpose: name game functions from the strings they reference, and record names from matches.

- Files: `bodecomp/strings.py`, `bodecomp/names.py`, `tools/export-strings.sh`, `tools/ghidra_scripts/ExportStringRefs.java`
- Input: the Ghidra project, `config/symbols.txt` and `config/functions.csv`.
- Output: `build/strings.tsv`, and `string` and `matched` names in `config/symbols.txt`.
- Commands: `tools/export-strings.sh` (server stopped), then `uv run python -m bodecomp.names stated|batch N|set|clear|check`. `names set 0xADDRESS NAME src/PATH.cpp` records a matched name.
- How: `strings.py` reads `build/strings.tsv` for `names.py` and `trivial.py`.
- Tests: `tests/test_strings.py`, `tests/test_names.py`, `tests/test_export_strings.py`.
- Decisions and findings: ADR-0008 (string names), ADR-0009 (names from matching), ADR-0011 (matched names), F-0032, F-0033.

## Ledger, README block and findings check

Purpose: report progress, and keep `docs/FINDINGS.md` in its form.

- Files: `bodecomp/ledger.py`, `bodecomp/readme.py`, `bodecomp/findings.py`
- Input: `config/symbols.txt`, `config/functions.csv`, `docs/FINDINGS.md` and `config/pre-public-commits.txt`.
- Output: `docs/LEDGER.md` and the progress block of `README.md`.
- Commands: `uv run python -m bodecomp.ledger [--check]`, `uv run python -m bodecomp.readme`, `uv run python -m bodecomp.findings check|summary`.
- How: `findings check` checks the form of each entry and that each `fixed (<commit>)` commit exists in git or in `config/pre-public-commits.txt`. `findings summary` lists the open and active findings for the session hook.
- Tests: `tests/test_ledger.py`, `tests/test_readme.py`, `tests/test_findings.py`.
- Decisions and findings: ADR-0016 (the pre-public commits).

## Agents and the session hook

Purpose: give each Claude session the current state, and give the agents only the tools they need.

- Files: `bodecomp/agent_tools.py`, `tools/session-start.sh`
- Input: git, GitHub (`gh` and `agent-skills`), `docs/FINDINGS.md`, `config/symbols.txt` and `ghidra/.sync-stamp`, and the ghidra-mcp schema from the running server or from a snapshot.
- Output: the text the hook prints; the `ghidra-read` tool block in `.claude/agents/matcher.md` and `.claude/agents/reviewer.md`, and the allowed tools in `.claude/settings.json`.
- Commands: `tools/session-start.sh` (run by the SessionStart hook in `.claude/settings.json`), `uv run python -m bodecomp.agent_tools`.
- How: the hook prints the generated state of the work (branch, running processes, Ghidra project freshness, Ghidra writer, pull requests, assigned issues, next command, last merged pull request), whether ghidra-mcp is up, and the open and active findings, in 40 lines or fewer (ADR-0021). When `build/overnight/run.json` holds a live unattended run, it adds one line from `bodecomp.overnight hook-line` (ADR-0023). The agents are `namer` (the only one that writes to Ghidra), `matcher` and `reviewer`, in `.claude/agents/`.
- Tests: `tests/test_session_start.py`, `tests/test_agent_tools.py`.
- Decisions and findings: ADR-0003, ADR-0007, ADR-0010, ADR-0015, F-0023, F-0025.

## An unattended run

Purpose: give a session that runs matcher batches for a set number of hours a clock, a progress count and a check before it starts ([ADR-0023](adr/0023-unattended-run.md)).

- Files: `bodecomp/overnight.py`
- Input: git, `config/functions.csv`, `orig/default.xbe`, `config/symbols.txt` and `ghidra/.sync-stamp`, the ghidra-mcp server, and GitHub through `gh`.
- Output: `build/overnight/run.json` (start, limit, run branch, counts at the start, end) and `build/overnight/log.tsv` (one row per `status` call), and the run branch `match/night-<YYYY-MM-DD>`.
- Commands: `uv run python -m bodecomp.overnight preflight|start <duration>|status|finish`.
- How: `preflight` runs eight checks and the gate of `AGENTS.md`. `start` makes the run branch from `main` when the checkout is clean and `main` equals `origin/main`, and keeps the first start time when a run is live. `status` prints the clock, a wrap-up line at 85 percent of the limit and a stall line after 30 minutes with no commit and no journal line. `finish` checks that the checkout is the head of the pull request, runs the gate and `ledger --check`, marks the pull request ready when they pass, and ends the run. The tests replace `gh`, the gate commands, the server check and the clock with fakes.
- Tests: `tests/test_overnight.py`, and `tests/test_overnight_settings.py` for the permissions of `config/overnight-settings.json`.
- Decisions and findings: ADR-0023, `docs/research/10-overnight-design.md` (R2 to R4).
