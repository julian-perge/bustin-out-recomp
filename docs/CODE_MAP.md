# Code map

Checked against the repo at commit 8260a0c on 2026-11-17.

Where to start reading in the repo's tooling. [ARCHITECTURE.md](ARCHITECTURE.md) gives the data flow, and [SUBSYSTEMS.md](SUBSYSTEMS.md) gives each part in detail.

## Questions

| Question | Start in | Then follow |
| --- | --- | --- |
| Why is a function not `matched`? | `bodecomp/match.py` | `config/functions.csv` (the `detail` column), the unit in `build/target/units/`, [WORKFLOW.md](WORKFLOW.md) "Matching" |
| Where does a name come from? | `config/symbols.txt` (the tier and evidence columns) | `bodecomp/names.py`, `bodecomp/libmatch.py`, `bodecomp/sync.py`, [ADR-0002](adr/0002-text-is-the-source-of-truth.md) |
| How is a source paired with its original function? | `bodecomp/match.py` | The address comment, `declared` and `generated` lines in [WORKFLOW.md](WORKFLOW.md) "Matching" |
| Where did a small function's source come from? | `bodecomp/trivial.py` | `src/game/trivial/`, [ADR-0012](adr/0012-gen-trivial-claims.md), [ADR-0013](adr/0013-no-hand-written-compiler-code.md) |
| How are the target objects cut from `.text`? | `tools/delink.sh` | `bodecomp/split.py`, `bodecomp/unitsplit.py`, `bodecomp/relink.py`, [ADR-0006](adr/0006-per-unit-objects-and-the-relink-gate.md) |
| Which compiler and flags build the sources? | `bodecomp/cl.py` | `bodecomp/match.py`, [ADR-0004](adr/0004-toolchain-and-default-flags.md), [ADR-0017](adr/0017-default-flags-gain-gx.md) |
| How is the Ghidra project rebuilt? | `tools/rebuild-ghidra.sh` | `bodecomp/sync.py`, `tools/create-functions.sh`, [WORKFLOW.md](WORKFLOW.md) "Rebuilding the Ghidra project from text" |
| Why is code at an address in no function? | `bodecomp/gaps.py` | `tools/create-functions.sh`, `tools/ghidra_scripts/CreateFunctions.java`, [WORKFLOW.md](WORKFLOW.md) "Function discovery" |
| What does a session see when it starts? | `tools/session-start.sh` | `.claude/settings.json`, `bodecomp/findings.py`, [ADR-0021](adr/0021-generated-session-state-and-ghidra-freshness.md) |
| Which tools may an agent call? | `.claude/agents/` | `bodecomp/agent_tools.py`, `.claude/settings.json` |
| How is progress counted? | `bodecomp/ledger.py` | `docs/LEDGER.md`, `bodecomp/readme.py` |
| Where are the clock and the progress of an unattended run? | `bodecomp/overnight.py` | `build/overnight/run.json`, `build/overnight/log.tsv`, [WORKFLOW.md](WORKFLOW.md) "An unattended run", [ADR-0023](adr/0023-unattended-run.md) |
| Is a fact about the binary already known? | [FINDINGS.md](FINDINGS.md) | `bodecomp/findings.py`, [adr/](adr/) |

## Top-level directories

| Directory | Role |
| --- | --- |
| `bodecomp/` | The Python package with every tool command. |
| `tools/` | Shell scripts that run Ghidra headless, the session hook, and the Ghidra scripts in `tools/ghidra_scripts/`. VC71 (`tools/xdk/`) and wibo (`tools/wibo/`) are unpacked here. |
| `src/` | The decompiled C++: `src/game/auto/` from matcher batches, `src/game/trivial/` from `bodecomp.trivial`, and `src/m0/` from M0. |
| `config/` | `symbols.txt` (names), `functions.csv` (match status), `m0_candidates.csv` and `pre-public-commits.txt`. |
| `docs/` | The method, workflow, findings, decisions, status, ledger and results files. |
| `spec/` | One spec per source issue, `spec/<issue>-<slug>.md`. |
| `tests/` | pytest tests and the builders of synthetic test files (`coffbuild.py`, `isobuild.py`, `xbebuild.py`). |
| `.claude/` | The agents, the session hook and the allowed tools. |
| `.github/` | The issue forms and the pull request template. |
| `orig/` | `default.xbe`, extracted from the user's disc image. |
| `build/` | Target units, built objects, string exports and logs. |
| `ghidra/` | The Ghidra project, rebuilt from text. |
| `xbox-sdks/` | The user's XDK archive. |
| `tasks/` | Plan scratch of the agent-skills workflow. |

[ARCHITECTURE.md](ARCHITECTURE.md), "Boundaries", lists the directories that git ignores.

## Entry points

The commands of [AGENTS.md](../AGENTS.md), "Commands":

- Tests and lint: `uv run pytest -q`, `uv run ruff check .`
- Names: `uv run python -m bodecomp.sync export|apply|check`
- Matching: `uv run python -m bodecomp.match [--check]`, `uv run python -m bodecomp.match candidates N`
- Trivial functions: `uv run python -m bodecomp.trivial generate [--max-size N]`, `uv run python -m bodecomp.trivial shapes [N]`
- Ghidra: `tools/ghidra-mcp-headless.sh`, `tools/rebuild-ghidra.sh`, `tools/delink.sh`, `uv run python -m bodecomp.relink`
- Code outside functions: `uv run python -m bodecomp.gaps report|candidates|starts`, then `tools/create-functions.sh`
- String names: `tools/export-strings.sh`, then `uv run python -m bodecomp.names stated|batch N|set|clear|check`
- Agent tools: `uv run python -m bodecomp.agent_tools`
- Progress: `uv run python -m bodecomp.ledger`, `uv run python -m bodecomp.readme`
- An unattended run: `uv run python -m bodecomp.overnight preflight|start|status|finish`

## Tests per area

| Area | Tests |
| --- | --- |
| Inputs and setup | `tests/test_setup_inputs.py`, `tests/test_xdvdfs.py`, `tests/test_xbe.py`, `tests/test_machine_paths.py` |
| Ghidra rebuild and name sync | `tests/test_symbols.py`, `tests/test_sync.py` |
| Delink and re-link | `tests/test_split.py`, `tests/test_unitsplit.py`, `tests/test_coffwrite.py`, `tests/test_relink.py` |
| SDK names | `tests/test_arlib.py`, `tests/test_libmatch.py`, `tests/test_libscan.py` |
| Matching | `tests/test_cl.py`, `tests/test_coff.py`, `tests/test_match.py`, `tests/test_m0.py` |
| Trivial functions | `tests/test_trivial.py` |
| Code outside functions | `tests/test_gaps.py`, `tests/test_create_functions.py` |
| String names | `tests/test_strings.py`, `tests/test_names.py`, `tests/test_export_strings.py` |
| Ledger, README and findings | `tests/test_ledger.py`, `tests/test_readme.py`, `tests/test_findings.py` |
| Agents and the session hook | `tests/test_session_start.py`, `tests/test_agent_tools.py` |
| An unattended run | `tests/test_overnight.py`, `tests/test_overnight_settings.py` |
| Docs | `tests/test_docs.py` |
| Package import | `tests/test_smoke.py` |

Run one area with `uv run pytest -q <files>`, and everything with `uv run pytest -q`.
