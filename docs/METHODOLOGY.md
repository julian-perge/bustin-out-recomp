# Method: a matching decomp with a recomp harness

This is the project's method document. It began as the design of 2026-10-10 and describes the repo as it is on 2026-11-17. Decisions made since 2026-10-10 are in `docs/adr/`, facts are in `docs/FINDINGS.md`, tool procedures are in `docs/WORKFLOW.md`, the rules every change follows are in `CODING_STANDARDS.md`, and the current state is in `docs/STATUS.md`.

## Intent

The goal is a byte-matching decompilation of the Xbox version of The Sims Bustin' Out: C++ that compiles with the original compiler to the exact bytes of the retail `default.xbe`. A static recompilation (xboxrecomp) is not the goal in itself. It serves as a runtime harness that checks the behavior of decompiled code and supplies evidence for naming.

Decisions made at the start:

| Question | Decision |
|---|---|
| End goal | Decomp harness: the recomp exists to support the decomp |
| Build host | One macOS machine. The compiler runs under wibo, and the harness is built with llvm-mingw and run under Wine (Sikarugir) |
| Bar for correctness | Byte-matching with the original compiler |
| Platform | Xbox is the matching target. The GameCube version is a donor of names, types and draft C++ |
| Compiler | The XDK 5558 compiler, from the user's own SDK archives. ADR-0004 set the default flags, and ADR-0017 added `/GX` |
| Workflow | AI agents do most of the matching in batches, and the user reviews. The repo was private until the decision of 2026-11-14 to publish it (ADR-0014, ADR-0016) |
| Structure | Functions first (approach 1 of 3). Grouping into source files comes later, and the harness comes in phase 2 |
| decomp.me | Not used. The command-line loop is the whole workflow |
| Git | Agents may make local commits and merge to local `main`. A push needs the user's say-so |

## Inputs

All inputs stay out of git (see `.gitignore`).

- `Sims, The - Bustin' Out (USA).iso`: retail Redump-style XGD1 image, 7,825,162,240 bytes, game partition at 0x18300000. `bustin_out.zip` is a TorrentZipped copy of the same ISO and is not needed.
- `default.xbe` from that ISO:
  - SHA-256 `c11eea3a1d5cbe932892bfb25e425d12cec229b9fc471563f1e368d607706725`, 3,211,264 bytes
  - title ID 0x45410043 (EA-067), region 0x1 (North America), built 2003-11-13
  - debug path `c:\eor\src2\games\sims\obj\sims_xbox_devsystem_release\Sims.exe`, which identifies the Edge of Reality engine
  - library stamps all 1.0.5558: XAPILIB, XBOXKRNL, LIBCPMT, LIBCMT, D3D8, XGRAPHC, DSOUND, XMV
  - `.text` at 0x00011000, size 0x232CE4 (2.2 MB). There are separate D3D, XGRPH, DSOUND, XMV and XPP sections
- `xbox-sdks/2003-06 - 5558.2 - SDK.7z`: contains `XDKSetup5558.2.exe`, which holds:
  - `XDK/xbox/bin/vc71/`: CL.Exe, C1.Dll, C1xx.Dll, C2.Dll, Link.Exe and the rest. The version strings read 13.10.3077 for the compiler and 7.10.3077 for the linker. They were read with a raw string scan. M0 confirmed the compiler's version, 13.10.3077 (`docs/m0-results.md`).
  - `XDK/xbox/lib/`: d3d8, dsound, xapilib, xgraphics, libc and the other SDK libraries
- `sims_bustin_out_gamecube.7z` in the repo root: the user's GameCube copy, not examined yet.

Findings from the strings, re-checked in Ghidra during M1 (details in `docs/m1-results.md`):

- There are no MSVC RTTI type names (`.?AV` or `.?AU`) anywhere in program memory, so class names don't come for free.
- Fifteen `.cpp` names appear, for example `.\Neighborhood.cpp`, `.\IFFResFile2.cpp`, `.\ObjectModule.cpp` and `.\e_graphics.cpp`, along with nine `c:\eor\src2\...` header paths. The earlier raw search counted sixteen.
- `.\aptauxpceorgl.cpp` is one of them, and code at 0x000FBC18 passes it to an allocation call, so EA's Apt UI library is in the Xbox build. The GameCube decomp's Apt work is a donor for it.

## Working rules

- **Use ghidra-mcp for analysis questions.** Anything about functions, references, strings, types or call graphs is answered through ghidra-mcp against the Ghidra project, not by guessing and not by text-searching the raw binary. A raw search finds bytes that look right but are not code or data references, which produces false findings. Raw byte searches are acceptable only before the Ghidra project exists, and their results stay marked preliminary until Ghidra confirms them.
- Text files in git are the source of truth. Ghidra is the workbench (see Architecture).
- When a claim says X caused Y, it says whether there is evidence or it is a guess.
- A toolchain problem that costs time becomes a GitHub issue labeled `needs-triage`, with the symptom, the cause (evidence or guess) and the fix.
- Repo documents are ASCII only.

## Architecture

```
ISO -> orig/default.xbe (hash-checked)
        |
   Ghidra (ghidra-xbe loader, headless via ghidra-mcp)
        |  auto-analysis + XDK library signatures + names from GC/Sims 2
        v
   config/*.txt  <---- sync ---->  Ghidra project
        |
   ghidra-delinker -> build/target/units/<unit>.obj   (original code, relocations recovered)
        |  bodecomp.relink: re-linking every unit must reproduce .text
        v
   src/**/*.cpp -> VC71 CL.Exe under wibo -> bodecomp.match (per function)
        |
   config/functions.csv -> bodecomp.ledger -> docs/LEDGER.md
```

Repo layout:

- `orig/`: files extracted from the ISO. Gitignored.
- `tools/xdk/`: VC71 and the SDK libraries unpacked from the 5558.2 archive. Gitignored.
- `config/symbols.txt`: address, name, size, name tier and the evidence for the name.
- `config/functions.csv`: matching status per function.
- `config/splits.txt`: source-file boundaries, planned for phase 3. It does not exist yet.
- `src/`: the decompiled C++. `src/game/trivial/` is written by `bodecomp.trivial generate`.
- `docs/m0-results.md` to `docs/m4-results.md` and `docs/thunk-trial-results.md`: the results of each milestone and batch.

The Ghidra project can always be rebuilt from `orig/default.xbe` plus the `config/` files. Agents edit in Ghidra through ghidra-mcp, and a sync script writes the changes back to `config/`, so nothing important lives only in the Ghidra project.

Tools, as checked on 2026-10-10:

- bethington/ghidra-mcp: targets Ghidra 12.2 on its `dev` branch (the v7.0.0 release targets 12.1.4), runs headless or with the GUI, and has write access.
- XboxDev/ghidra-xbe: the XBE loader, latest build 2026-10-16, for Ghidra 12.1.4. It has no build for Ghidra 12.2, so it is built from source at b5171ca against the installed Ghidra.
- boricj/ghidra-delinker-extension: v0.9.3, with a build for Ghidra 12.2. It exports x86 COFF objects.
- decompals/wibo: 1.2.0, ships a macOS binary.

## Phase 1: analysis and naming

**Load.** Ghidra opens `default.xbe` with ghidra-xbe, and kernel imports are named by ordinal. The function count from auto-analysis is cross-checked against the xboxrecomp disassembler, which found 14,083 functions in Mercenaries, a game of similar size.

**Name tiers.** Every name in `symbols.txt` carries a tier and its evidence. A name can only be raised to a higher tier when there is new evidence for it.

1. `sdk` (exact). Each function's bytes are compared with every function in the XDK 5558.2 .lib files, skipping bytes at relocation sites (bodecomp/libmatch.py). That is the same evidence Ghidra's Function ID uses, done without a Ghidra project of the libraries. This names the SDK code: the D3D, DSOUND, XMV, XGRPH and XPP sections and the C runtime inside `.text`. SDK functions are never decompiled. The final build links the original `.lib` files.
2. `gc` (strong). Names carried over from the Sims 2 GameCube symbol map (natebag/Sims2DECOMP, 36,913 symbols) and from daftblazer/bustin-out-decomp. Size alignment does not work across different CPUs and compilers, so matches rely on evidence that survives recompiling: shared string references, shared numeric constants, call-graph neighbors of functions already named, and vtable shape. A `gc` name needs two independent kinds of evidence, and both are recorded.
3. `string` (medium). Names inferred from a function's own strings (ADR-0008).
4. `auto`. Ghidra's `FUN_xxxxxxxx` placeholders.

A fifth tier, `matched`, came later (ADR-0011). A function whose C++ compiles to its original bytes takes the name the compiler gives it, with its source file as evidence. After M2b, functions are named when they are matched, not in separate naming passes (ADR-0009). `gc` naming is deferred until its revisit condition holds (F-0029).

**Types.** Struct and class layouts start from daftblazer's headers. GCC 2.95 and MSVC 7.1 can disagree on vtable pointer placement, bitfield layout and empty-base handling, so each imported type is checked against the field offsets the Xbox code actually uses before anyone relies on it.

**Relocations.** Ghidra's references feed the delinker after a review for constants that only look like addresses. The check is mechanical: re-linking every target object at its original address must reproduce `.text` byte for byte.

## Phase 1: the build and matching loop

**Build.** `tools/delink.sh` writes one target object per unit to `build/target/units/` (ADR-0006). `uv run python -m bodecomp.match` compiles every `src/**/*.cpp` except `src/m0` with `tools/xdk/xbox/bin/vc71/CL.Exe` under wibo, compares each function with its target unit, and writes `config/functions.csv`. `docs/WORKFLOW.md`, "Matching", gives the rules of the comparison.

**Symbol pairing.** A function's MSVC decorated name only exists once its C++ signature has been written. Each decompiled function therefore carries an address comment (`// 0x0012F3A0`), and `bodecomp.match` reads the compiled object to pair that function with its target unit. A `declared` line gives an address to a constructor, destructor or override that is not matched, and a `generated` line claims a thunk or a deleting destructor (`docs/WORKFLOW.md`).

**Compiler flags.** M0 matched 19 of 20 hand-written leaf functions at one flag set (`docs/m0-results.md`). The default is `/O2 /G7 /arch:SSE /GX` (ADR-0004, ADR-0017).

**Source layout in phase 1.** Matcher batches write files named by an address or a block of addresses to `src/game/auto/`, `bodecomp.trivial` writes `src/game/trivial/`, and the M0 functions are in `src/m0/`. Only each function's own compiled bytes are compared, so which file a function sits in does not matter yet. The exception is when VC7.1 inlines a helper or allocates registers differently because of a neighboring function. In that case the helper moves next to its caller, following halo-1's rule that callers are made exact first.

**Status values in `functions.csv`:**

| Status | Meaning |
|---|---|
| `matched` | Identical bytes and identical relocations |
| `nonmatching` | The best percentage so far, with the C++ kept |
| `parked` | Stopped after five honest attempts at the source's structure. Recorded with a blocker class from halo-1's `docs/matching_methodology.md`: source shape, integer width, register tie, scheduling, or unclassified |
| `error` | No check reached a compiler-generated function at the claimed address |

SDK functions get no row: their status comes from their tier in `config/symbols.txt`.

**Rules taken from halo-1.** No inline assembly, no `#pragma` tricks, and no code whose only purpose is to steer the compiler. A match that relies on any of these does not count. Nothing the compiler generates is written by hand (ADR-0013). Rule `S1` of `CODING_STANDARDS.md` states both.

**Progress.** `uv run python -m bodecomp.ledger` writes `docs/LEDGER.md` from `config/symbols.txt` and `config/functions.csv`: functions and bytes per status, with SDK code in its own rows. `uv run python -m bodecomp.readme` writes the progress block of `README.md`.

## Phase 1: the agent workflow

Work is tracked in GitHub issues. `docs/agents/workflow.md` gives the stages, from an idea to a merged pull request, and the labels. Each change is checked against `CODING_STANDARDS.md`.

**Roles:**

- Namer: Works in Ghidra through ghidra-mcp, one engine or game module at a time. It assigns `gc` and `string` names with their evidence and runs the sync. Only one namer writes to the Ghidra project at a time.
- Matcher: Takes a batch of 20 functions from `match candidates 20 --min-size 17`. It reads Ghidra through ghidra-mcp without writing to it, and writes C++ in its own git worktree.
- Reviewer: A separate agent pass, then the user. It checks the change against rules `S1` to `S4` of `CODING_STANDARDS.md`: plausible source, evidence for claims, evidence for names, and staying in the task.

**What a matcher gets for each function:** the target assembly, Ghidra's decompiled version (through ghidra-mcp), daftblazer's GameCube C++ if that function is matched there, the context header, and any callers and callees already decompiled.

**Order of work.** Leaf functions come first and work moves up the call graph, because a caller's code depends on its callees' signatures. Within a module, the smallest functions go first. Only one matcher works in a module at a time.

**The loop.** Write C++, run `bodecomp.match`, read the first difference, adjust. After five honest attempts at the source's structure, the function is parked with its blocker class and the best attempt is kept.

**The merge gate.** A batch merges into local `main` only when:

1. `bodecomp.match --check` passes, and every function that was already matched still matches,
2. `pytest`, `ruff check`, `findings check` and the other checks of the full gate in `docs/WORKFLOW.md` pass, and
3. the reviewer pass is clean.

In an unattended run ([ADR-0023](adr/0023-unattended-run.md)), a batch merges into the run branch instead of `main`, by the same gate. The run branch goes to `main` through one pull request, and the user merges it.

The results of each batch, with what matched, what was parked and why, go into the results file of its milestone, such as `docs/m4-results.md` or `docs/thunk-trial-results.md`.

**The user's part.** Read the pull requests, the results files and `docs/LEDGER.md`, spot-check the source, and decide anything an agent flags as unclear, such as a name with conflicting evidence or a suspected original bug.

## Phase 2: the recomp harness (M6)

The decompiled C++ compiles to 32-bit Xbox code, while the recomp host is a 64-bit program. Matched functions therefore reach the harness through a rebuilt XBE, not by being linked in directly.

1. Rebuild the XBE. Link the matched objects, plus target objects for everything else, at their original addresses, and wrap the result back into an XBE. While all code is either matched or original, the result must be byte-identical to `orig/default.xbe`, which checks the whole build end to end.
2. Run it in the harness. Lift the rebuilt XBE with xboxrecomp, starting from KraftMacAndChee/Mercenaries-Recompiled on the PR #2 branch (`ports/linux-crosscompile-and-ssaa`), the macOS build path already verified to compile. Build with llvm-mingw under `env -u CFLAGS -u CPPFLAGS -u CXXFLAGS -u LDFLAGS` and run under Sikarugir. Known work:
   - XDK 5558 differences. The kernel version 5849 is hardcoded in `src/kernel/kernel_bridge.c` and `src/kernel/kernel_xbox.c`. SDK function names come from phase 1's `sdk` tier.
   - The macOS address fix, applied in source: the arena search starts at 0x7000000000.
   - The black screen seen with the Clang build of Mercenaries, which gets debugged here.
3. Use it for:
   - differential runs: scripted scenarios with call traces and memory snapshots, comparing the original with a rebuild that contains a `nonmatching` function
   - runtime traces of which functions run during which game actions, as naming evidence

## Phase 3: source files and data (M7)

Group matched functions into their original source files using:

- the GameCube splits and the Sims 2 map's object names
- the function order in the XBE (MSVC lays out functions in object order)
- the order of the `.rdata` string pools
- the `.cpp` names found in the strings

Then move to a halo-1-style csplit layout and start matching `.data` and `.rdata`.

## Milestones

| Milestone | Exit condition |
|---|---|
| M0 Toolchain | VC71 runs under wibo, and 20 hand-written leaf functions match with a recorded flag set. If that fails, the cause is identified |
| M1 Analysis | The Ghidra project rebuilds from text, SDK functions are named, re-linking the target objects reproduces `.text` byte for byte, and the preliminary raw-search findings are re-checked in Ghidra |
| M2 Naming | A first naming pass over the engine and game modules, with the share of named game functions reported per tier. After M2b, functions are named when they are matched (ADR-0009) |
| M3 First batch | One matcher batch merged through the full gate, with lessons folded back into the agent prompts |
| M4 Steady state | Batches run routinely and progress is tracked in `docs/LEDGER.md`. No percentage target is set until M3 shows the pace |
| M5 Larger functions | A byte shape among functions larger than the gen_trivial set is found, and one matcher batch of that shape merges through the full gate, with its cost per matched function recorded |
| M6 Harness | The rebuilt XBE is byte-identical, and the harness reaches the main menu under Wine on macOS |
| M7 Layout | Source-file splits and data matching are under way |

## Risks

| Risk | Mitigation |
|---|---|
| False relocations | The re-link check and the relocation comparison of `bodecomp.match` |
| Wrong names carried over from GameCube | The two-evidence rule and the tiers |
| The harness inherits the Mercenaries black screen | Phase 2 does not block matching. If it stalls, xemu can run the rebuilt XBE for behavior checks, which needs BIOS and MCPX dumps from the user's console |
| Two agents writing to Ghidra at once | Only one namer writes at a time |
| Copyrighted files in git | The ISO, the XDK and anything extracted stay gitignored |

## Testing the tools

The project's own scripts are tested with pytest on small synthetic COFF fixtures: the Ghidra sync, symbol pairing, the progress report and the regression gate. Tests never read the ISO. The tests that compile with VC71 run only when `tools/xdk/` and `tools/wibo` are set up, and are skipped otherwise.

## References

- bnunu/halo-1: an Xbox matching decomp using csplit, project_x86.py, wibo and objdiff with VC7 from XDK 3911. See `docs/matching_methodology.md` for its blocker classes and the rule that source must be plausible, not just matching.
- doldecomp/melee: the per-function workflow in `docs/getting_started.md`.
- n64decomp/mk64: splat-based N64 layout.
- daftblazer/bustin-out-decomp: the GameCube `G4ME69` matching decomp, built with SN ProDG GCC 2.95.2. Its `tools/align_sims2.py` aligns functions with The Sims 2.
- natebag/Sims2DECOMP: The Sims 2 GameCube symbol map.
- KraftMacAndChee/Mercenaries-Recompiled: the xboxrecomp toolkit. See `docs/GETTING_STARTED.md` for new titles.
- decomp.me and decompme_compilers: kept as a reference for how compilers are packaged and not used in the workflow. Note that its `msvc7.1` entry downloads a file named `msvc7.0.tar.gz`. Whether that is only a naming slip has not been checked.
