# dx-ball deep dive

Source: the clone of N0zoM1z0/dx-ball at `~/git/N0zoM1z0/dx-ball`, HEAD `e2a633f` (2026-11-10). Citations with the prefix `dx-ball/` point into that clone. A citation of the form `dx-ball/HASH:path:LINE` is the file at an older commit (`git show HASH:path`). A commit is cited as its short hash and subject. "Computed" marks a number that a read-only command over the clone gave, and that no file in the clone states. Nothing from the clone was run.

## Summary

- dx-ball is a byte-matching reconstruction of a 1996 Windows game. One Codex session at a time wrote it, under the Codex `/goal` command, in 16 days and 686 commits.
- It did not run unattended. The history records at least six human actions: stops, resumes and one authorization (section 7).
- The repo has no hook, no time limit, no budget, no stop rule and no queue file. Continuation came from `/goal`, and resume state came from a hand-edited handoff file.
- The parts worth copying are the checks: pinned inputs, a one-command compare with an exit code, hash-bound acceptance rows, negative results recorded as commits, and an explicit demotion rule.
- The claim "270 of 270 functions, 84,968 bytes" agrees with the ledgers in git. The byte equality itself is UNVERIFIED from git, because the original EXE, the compiler and all compare reports are untracked.

## 1. What the project is

- Goal: `dx-ball/README.md:3` "This project reconstructs English DX-Ball v1.07 as readable C/C++ using the"
- Agent: `dx-ball/README.md:4` "original executable and resources. Codex uses [REA](https://github.com/morluto/rea)"
- Codex version: `dx-ball/docs/SETUP.md:60` "Codex 0.128.0 or newer:"
- All 691 commit subjects start with `gpt-6.1-sol: ` (Computed: `git log --format=%s | rg -vc '^gpt-6.1-sol: '` finds none). The prefix is an instruction: `dx-ball/AGENTS.md:70` "Commit and push verified checkpoints to" That `gpt-6.1-sol` names a real model is UNVERIFIED. No commit has a co-author trailer.
- Size (Computed): 691 commits, 811 tracked files. First commit `700a00e` "gpt-6.1-sol: Pin DX-Ball 1.07 target and establish attested Ghidra workflow" on 2026-10-07. The last change to the match ledger is `ecfc475` "gpt-6.1-sol: Recover the exact PCX decoder and complete all authored matches" on 2026-10-22.
- The last commit rewrote the docs. `e2a633f` "gpt-6.1-sol: simplify repository retention and public checks" changed 356 files and deleted 10,216 lines (Computed: `git show --stat e2a633f`). The docs at HEAD describe the end state. The loop as it ran is only in older commits.
- The project lead also works on REA. This is a statement of the video ([02-video.md](02-video.md), 07:15) and of the community list ([08-lists-and-experiments.md](08-lists-and-experiments.md)). The dx-ball clone does not state it.

## 2. Agent instructions

The repo holds one `AGENTS.md` (72 lines) and five files in `docs/agent/`. It has no `CLAUDE.md`, `.claude/`, `.codex/`, skill, hook, pre-commit config or `.mcp.json` (Computed: `git ls-files | rg -i '(^|/)(CLAUDE|.claude|.codex|.agents|.cursor|.mcp|skills?|prompts?)(/|.|$)'` prints nothing).

What `AGENTS.md` orders:

- Read order: `dx-ball/AGENTS.md:9` "Read [the handoff](docs/agent/HANDOFF.md), [workflow](docs/agent/WORKFLOW.md) and the"
- Candidate rule: `dx-ball/AGENTS.md:23` "- Freeze each distinct candidate, compile it once and compare the complete"
- The agent selects its checks: `dx-ball/AGENTS.md:26` "- Select checks for the changed behavior. Status and documentation work use"
- Source quality: `dx-ball/AGENTS.md:18` "assembly replacements, padding and fake locals out of exact reconstruction."
- One heavy job at a time: `dx-ball/AGENTS.md:35` "Run one compiler/provider/Wine job at a time on one allowed CPU, with"
- Ledgers follow claims: `dx-ball/AGENTS.md:61` "Update affected ledgers when claims change."
- CI needs no private input: `dx-ball/AGENTS.md:66` "Default CI must work in a clean checkout without originals or private tools. Keep"

Rules about autonomy and stopping are in `docs/agent/SOURCE_CANDIDATE_SEARCH.md`. The agent wrote them after a human unblocked it (section 7):

- Standing permission: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:7` "the same permission boundary. This is standing authorization, not a request for"
- The agent sets its own limits: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:91` "The agent may choose the finite domains, useful batch size and stopping limits"
- No new gates: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:97` "### Proportionate execution, not accumulating gates"
- A reviewer is optional: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:104` "tools for a concrete uncertainty, not prerequisites for continuing work."
- After a batch, continue: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:157` "After a batch, record what it ruled out and select the next eligible bounded"
- Do not block on the same question: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:160` "a reason to request the same authorization or mark the goal blocked."
- No endless search: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:125` "Do not turn one failed family into an unbounded automatic enumeration."
- What stays forbidden: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:50` "The following remain prohibited: copied machine code, assembly, fake or unused"
- Only an external blocker stops the work: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:162` "source optimality. Report genuine external/authority blockers separately;"

The start prompt is in the repo. It is a Codex goal:

- `dx-ball/docs/SETUP.md:125` "/goal Reconstruct English DX-Ball v1.07 from original/DXBALL.EXE as readable,"
- `dx-ball/docs/SETUP.md:129` "Read AGENTS.md, docs/agent/HANDOFF.md, and docs/agent/WORKFLOW.md. Continue from"
- `dx-ball/docs/SETUP.md:143` "Record verified results in the match ledgers, progress, and handoff. Keep code"
- `dx-ball/docs/SETUP.md:148` "Report completed game flows, unresolved failures and the next useful check."
- Controls: `dx-ball/docs/SETUP.md:153` "Enter `/goal` to view the objective, `/goal pause` to pause work, and"

The prompt and the instruction files hold no duration, budget or stop time (Computed: `rg -n -i 'hour|deadline|budget|timeout' AGENTS.md docs/agent/HANDOFF.md docs/agent/WORKFLOW.md docs/SETUP.md` prints nothing).

## 3. Ghidra and REA configuration

dx-ball does not let the agent harness start the MCP server. A Node script in the repo is the MCP client, and the agent calls it through a shell wrapper.

- Entry: `dx-ball/docs/agent/REA.md:3` "Use `scripts/rea` for new binary analysis. The lock pins REA 6.5.0, Ghidra 12.1.4,"
- The client starts REA over stdio: `dx-ball/scripts/rea-session.mjs:56` "args: [resolve(root, '.tools/rea-runtime/node_modules/rea-agents/scripts/rea.mjs'), 'mcp'],"
- It allows a fixed list of tools (23 names, Computed): `dx-ball/scripts/rea-session.mjs:38` "const allowed = new Set(['binary_overview', 'binary_session', 'analyze_function',"
- Per-call timeouts: `dx-ball/scripts/rea-session.mjs:70` "{timeout: compilerTarget ? 930000 : 360000,"
- A failed request writes its index to a file: `dx-ball/scripts/rea-session.mjs:152` "save('failure.json', {completed, request: requests[completed], message: String(error)});"
- REA is installed from a lock, not globally: `dx-ball/scripts/bootstrap-rea.py:19` "--registry=https://registry.npmjs.org" with the one dependency `dx-ball/config/rea/package.json:3` "rea-agents"
- Every call re-checks the tool hashes: `dx-ball/scripts/rea.py:34` "REA package/dependency bytes changed; bootstrap the pinned installation" and `dx-ball/scripts/rea.py:37` "REA Ghidra input changed: {name}"
- Queries on another file are refused: `dx-ball/scripts/rea.py:79` "REA query must use the configured original/DXBALL.EXE"
- The Ghidra heap is small on purpose: `dx-ball/docs/agent/REA.md:5` "heap to 256 MiB. Installations may share immutable Factory tools; keep this"
- One session at a time, by file lock: `dx-ball/scripts/legacy_toolchain.py:90` "fcntl.flock(stream, fcntl.LOCK_EX)"

A second, older path runs plain headless Ghidra through `scripts/ghidra.py` and five Java scripts in `scripts/ghidra/`. It reopens the project read-only: `dx-ball/scripts/ghidra.py:371` "-readOnly" and `dx-ball/scripts/ghidra.py:372` "-noanalysis"

### How the Ghidra state is "attested"

"Attested" means: check known hashes before the run, check again inside Ghidra, and fail when a success marker is missing. It is not a signature.

1. `config/target.toml` holds the size, SHA-256, MD5 and PE fields of the EXE: `dx-ball/config/target.toml:7` "756da1ba09edce716d5bf8770320ca0d5ed4e525672b6bb605b9bdb4b88972ba"
2. Python verifies the file: `dx-ball/scripts/verify-target.py:2` "Verify the canonical DX-Ball v1.07 executable and its PE mapping."
3. Python reads six 16-byte samples from `.text`: `dx-ball/scripts/ghidra.py:147` "Return distributed target-file bytes at mapped .text addresses."
4. A Ghidra script compares what Ghidra loaded: `dx-ball/scripts/ghidra/VerifyTarget.java:1` "// Fail-closed attestation for a loaded DXBALL program." and `dx-ball/scripts/ghidra/VerifyTarget.java:56` "String actualHash = currentProgram.getExecutableSHA256();"
5. On a mismatch the script aborts the headless run: `dx-ball/scripts/ghidra/VerifyTarget.java:16` "setHeadlessContinuationOption(HeadlessContinuationOption.ABORT);"
6. Python fails unless the marker is in the output: `dx-ball/scripts/ghidra.py:271` "Ghidra did not emit the exact target-attestation success marker"
7. A smoke test compares bytes read through REA with bytes read from the PE file: `dx-ball/scripts/verify-rea.py:43` "REA loaded-byte observation disagrees with independent PE bytes"

In git: the manifests, the lock files, the ledgers, the scripts and the notes. Not in git: `dx-ball/.gitignore:1` "original/", `dx-ball/.gitignore:2` ".tools/", `dx-ball/.gitignore:3` ".analysis/", `dx-ball/.gitignore:4` "ghidra-project/", `dx-ball/.gitignore:5` "build/".

Limits of the attestation:

- It covers the input file and the tool bytes. It does not cover the analysis result. No script rebuilds the Ghidra project and compares it with `config/functions.csv` (Computed: `rg -n 'functions.csv' scripts/ghidra.py` shows one read and one export target).
- The first function list was provisional: `dx-ball/700a00e:AGENTS.md:10` "Treat the 528 imported function extents as provisional, including embedded"
- The REA game session does not compare the opened binary's hash. Only compiler targets get that check: `dx-ball/scripts/rea-session.mjs:93` "if (compilerTarget && open.result.sha256 !== expectedTargetHash) {"
- The notes cite REA evidence IDs (`ev_` and 64 hex digits) in 253 of 344 notes (Computed). The snapshot that resolves them is untracked, so every ID is UNVERIFIED.

## 4. The loop

No script runs the loop and no queue file exists. The loop is prose. The clearest version is the nine-step list of an old file:

1. `dx-ball/89505c4:docs/RE_WORKFLOW.md:7` "1. Read the handoff and relevant owner evidence; inspect `git status`."
2. `dx-ball/89505c4:docs/RE_WORKFLOW.md:8` "2. Verify target, toolchain, and tracking. Use `scripts/rea` for new binary"
3. `dx-ball/89505c4:docs/RE_WORKFLOW.md:11` "3. Select a related batch of entries from `config/functions.csv`. Reconcile control flow,"
4. `dx-ball/89505c4:docs/RE_WORKFLOW.md:15` "4. Inspect exact instructions, data references, producers, and independent"
5. `dx-ball/89505c4:docs/RE_WORKFLOW.md:18` "5. Reconstruct natural shared C source with explicit state ownership and ABI."
6. `dx-ball/89505c4:docs/RE_WORKFLOW.md:20` "6. Once the batch's source is stable, replay its target-machine differential"
7. `dx-ball/89505c4:docs/RE_WORKFLOW.md:27` "7. Promote exactness only after a cold, configured zero-difference replay."
8. `dx-ball/89505c4:docs/RE_WORKFLOW.md:29` "8. Update the knowledge base and handoff, validate ledgers, regenerate progress,"
9. `dx-ball/89505c4:docs/RE_WORKFLOW.md:31` "9. Periodically seal accepted inputs, products and diagnostics, then run"

Facts about the loop:

- The unit of work is a batch of related functions, not one function. The agent set this rule three hours after the first commit: `c6a7786` "gpt-6.1-sol: Batch reconstruction before cold replay" and `dx-ball/c6a7786:AGENTS.md:41` "Do not cold-replay after each individual function. Reuse completed reports"
- A failed compare gives the next analysis question: `dx-ball/docs/MATCHING.md:16` "to REA's instructions, callers and data consumers to resolve those questions,"
- The next target comes from the status column of `config/functions.csv` and from a free-text line in the handoff, for example `dx-ball/89505c4:docs/RE_HANDOFF.md:29` "Next: complete projectile and fire-effect list lifecycles as a coherent family;"
- A planned multi-agent claim table was dropped: `dx-ball/scripts/validate-tracking.py:231` "one-session claims ledger must be header-only" That it was planned for several agents is an inference from the name.
- A typical commit holds source, ledger, note and handoff together (Computed from `git log --numstat`: median 8 files per commit; 537 of 691 commits touch `docs/research/`, 545 touch the handoff).

## 5. Verification gates

### The compiler

- Visual C++ 4.0 runs under Wine: `dx-ball/config/tools.lock.toml:22` "Microsoft (R) 32-bit C/C++ Optimizing Compiler Version 10.00.5270 for 80x86" and `dx-ball/scripts/legacy_toolchain.py:65` "xvfb-run"
- Compiler files are hash-pinned: `dx-ball/scripts/legacy_toolchain.py:51` "toolchain hash mismatch: {name}"
- Each compiler call has a timeout: `dx-ball/scripts/legacy_toolchain.py:67` "timeout=120"
- The compiler identity is a candidate, not a proof: `dx-ball/config/tools.lock.toml:24` "observed-candidate"
- Flags are set per source file. The manifest has 134 builds over 134 source files and 8 flag sets (Computed from `config/match-units.toml`). The policy allows the agent to split files to get this: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:37` "translation-unit ownership/splitting may also be reconstructed as bounded"

### The compare

- One command: `dx-ball/docs/MATCHING.md:31` "scripts/repo-python scripts/replay-exact-units.py \"
- It builds from a clean state: `dx-ball/scripts/replay-exact-units.py:2` "Cold-build canonical shared source and compare every byte after relocations."
- The relocation set of the object must equal the set that the manifest declares: `dx-ball/scripts/replay-exact-units.py:48` "if sorted(actual_keys) != sorted(expected_keys):"
- Each relocation field gets the declared original address, then every byte is compared: `dx-ball/scripts/replay-exact-units.py:73` "differences = [i for i in range(max(len(contents), len(target)))"
- No relocation is masked: `dx-ball/config/match-units.toml:1` "# Full one-function COMDAT extents; every relocation is applied, none masked."
- Output is one line per unit, EXACT or DIFF with the count of different bytes: `dx-ball/scripts/replay-exact-units.py:163` "{result['difference_count']} differing bytes,"
- The exit code is 1 when a unit differs: `dx-ball/scripts/replay-exact-units.py:167` "return 0 if all(r["
- Definition of exact: `dx-ball/docs/MATCHING.md:10` "An exact unit has zero differences across that complete comparison."
- The scope is function bodies and attached metadata. The linked image is not byte-equal to the original: the rebuilt EXE has 166,400 bytes (`dx-ball/docs/research/CURRENT_VC4_BUILD.md:14` "166,400") and the original has `dx-ball/config/target.toml:6` "size = 158208"

### Behavior tests ("differential" tests and "oracles")

- The oracle is an emulator that runs the original code: `dx-ball/tests/target_oracle.py:1` "Execute unmodified target x86 functions with controlled dependency boundaries."
- The other side is the same source, built for the host as a shared library: `dx-ball/CMakeLists.txt:10` "add_library(dxball_core SHARED"
- A test calls both with the same inputs and compares results and state: `dx-ball/tests/test_core_queues_differential.py:69` "assert result == target_result, (name, result, target_result)"
- 235 of the 270 authored functions have such a test (Computed from `config/semantic-acceptance.csv`). For the other 35 only the byte match exists.

### Guards against a false match

- Each accepted row stores the hashes of its inputs. The ledger check fails when a source, header or manifest changed: `dx-ball/scripts/validate-tracking.py:227` "accepted exact input changed; replay and refresh evidence: {field}" and `dx-ball/scripts/validate-tracking.py:229` "accepted exact build input set changed; replay required"
- A row must name the pinned target and compiler: `dx-ball/scripts/validate-tracking.py:214` "exact row uses another target"
- A function called from several units must have one declared address: `dx-ball/scripts/validate-tracking.py:56` "function target disagrees with declared entry:"
- The agent found a real false match and added a check. A local label moved by five bytes while all compared bytes stayed equal: `dx-ball/docs/research/exact/EXACT_LOCAL_TARGET_GUARD.md:19` "redirects its linker destination by five bytes. Code and relocation-table bytes" The check: `dx-ball/scripts/replay-exact-units.py:40` "exact local target differs for {binding['symbol']}:" Its test: `dx-ball/tests/test_exact_local_targets.py:57` "def test_changed_local_definition_cannot_claim_exact(self):"
- Demotion is explicit. Eight commits lowered the count of exact rows (Computed). The body of `d1ab2ff` "gpt-6.1-sol: Restore sprite-bank byte-count wrap semantics" says that two functions "explicitly lose exact status".

### What the gates do not do

- CI runs no compiler and no compare: `dx-ball/scripts/ci.py:2` "Fast public checks; no originals, analysis packages or private tools required." Its one step: `dx-ball/.github/workflows/ci.yml:23` "run: scripts/repo-python --stdlib scripts/ci.py --public"
- No script writes `config/matches.csv`. `rg -n 'matches.csv|semantic-acceptance' scripts tests` finds only readers. How the rows were made is UNVERIFIED. A row with correct hashes and a difference count of 0 passes CI whether or not a compile happened.
- The comparator tests are not run by CI or by any script (Computed: `rg -n 'test_exact_local_targets|test_function_target_consistency' scripts .github` finds nothing).
- No hook runs a check before a commit.

### One function, end to end: 0x00413410

1. Ledger row: `dx-ball/config/functions.csv:242` "0x00413410,146,0x004134A1,FUN_00413410,dxball_append_projectile,core,exact,100.00,fastcall"
2. Source: `dx-ball/src/list_initializers.cpp:138` "DxBallInt DXBALL_FASTCALL dxball_append_projectile(DxBallProjectileList *list)"
3. Manifest unit: `dx-ball/config/match-units.toml:5626` "[units.append-projectile]" with `dx-ball/config/match-units.toml:5629` "target_address = 0x413410"
4. Behavior test: `dx-ball/tests/test_core_queues_differential.py:21` "ENTRIES = {'append_projectile':0x413410, 'begin_projectiles':0x410130,"
5. Compare: `dx-ball/scripts/replay-exact-units.py:159` "result = compare(output, unit, pe)"
6. Acceptance row: `dx-ball/config/matches.csv:242` "0x00413410,append-projectile,src/list_initializers.cpp,aade830666b668eae754bd82f590ac8d58e5f6fe713bfcd05c2a211a8def4580"

### The 270 of 270 claim

- Claim: `dx-ball/README.md:30` "All **270/270 authored game functions** and **84,968/84,968 authored code bytes**"
- Recomputed from the ledgers in git: `config/function-origins.csv` has 553 rows, 270 of them `authored`. All 270 are in `config/matches.csv` with a difference count of 0, and their sizes sum to 84,968.
- So the ledgers agree with the README. The byte equality is UNVERIFIED: the compare needs the EXE, the compiler and Wine, and no compare report is tracked.
- "Authored" is the project's own class. 261 runtime entries are outside the 270, and the build links original library members: `dx-ball/README.md:87` "The build links 138 source objects, three integration objects and 19 original"

## 6. Progress tracking

- Ledgers in `config/`: `dx-ball/config/README.md:6` "| `functions.csv` | Independent original entries, extents and recovered names |" and `dx-ball/config/README.md:9` "| `match-units.toml`, `matches.csv` | Complete compiler comparisons and accepted exact units |"
- A status command for a new session: `dx-ball/docs/agent/HANDOFF.md:55` "scripts/repo-python scripts/report-reconstruction-status.py --summary"
- The progress page is generated: `dx-ball/scripts/progress.py:2` "Generate authored completion, verification results and the progress graphic." The README numbers are typed by hand.
- Commit subjects use a small set of verbs (Computed): restore 201, recover 130, verify 42, close 40, record 28. "Close" marks a rejected hypothesis that is committed as a result, for example `0f37699` "gpt-6.1-sol: close the embedded-list member-call hypothesis"
- Commit bodies carry counts, for example the body of `bcc03fc` "gpt-6.1-sol: Recover exact polygon controllers through real local declarations" has "263/270 authored exacts, 77702/84968 bytes".
- `docs/research/` holds 344 notes: 70 at the top level by subsystem and 274 in `exact/` by function family (Computed). No template file and no checker exist. A typical note has a title, a paragraph with counts and addresses, a table of routines, an evidence section and the ledger change, for example `dx-ball/docs/research/exact/EXACT_SOUND_BUFFERS.md:9` "| Routine | Address | Bytes | Compiler result |"
- The hand-written index is partial: 206 of 273 notes in `exact/` are not named in `exact/README.md` (Computed). The ledgers are the real index: their evidence column names the note of each function, for example `dx-ball/config/functions.csv:2` "docs/research/MIDI_OWNER.md"

Ledger growth (Computed: rows of `config/matches.csv` at the last commit of each day, header included):

| Day | Commits | Rows |
| --- | ---: | ---: |
| 2026-10-07 | 28 | 41 |
| 2026-10-08 | 56 | 37 |
| 2026-10-09 | 18 | 64 |
| 2026-10-10 | 56 | 159 |
| 2026-10-11 | 93 | 207 |
| 2026-10-12 | 36 | 230 |
| 2026-10-13 | 48 | 264 |
| 2026-10-14 | 63 | 349 |
| 2026-10-15 | 30 | 363 |
| 2026-10-16 | 38 | 381 |
| 2026-10-17 | 67 | 395 |
| 2026-10-18 | 64 | 396 |
| 2026-10-19 | 13 | 393 |
| 2026-10-20 | 28 | 395 |
| 2026-10-21 | 28 | 403 |
| 2026-10-22 | 20 | 416 |

From 2026-10-17 to 2026-10-20 the count did not rise, while 105 commits were made on the last three of those days.

## 7. How a session kept going, and where it did not

### Cadence (Computed from commit times)

- 686 of 691 commits fall in 16 days. The median gap between commits is 20.4 minutes.
- 18 runs with every gap under 30 minutes last 2 hours or more. The longest: `4c24034` to `6fc6442`, 2026-10-11 09:09 to 19:33 (+08:00), 48 commits in 10.4 hours.
- Every clock hour has at least 18 commits. Commit times do not show whether a person was present.
- The window nearest to "work for 8 hours": 2026-10-21 23:32 to 2026-10-22 08:05 (+08:00), 15 commits from `f823bde` "gpt-6.1-sol: Recover exact frame waiting in its own source owner" to `ecfc475`, which completes the 270. It follows a human resume. Whether a person was present is UNVERIFIED.

### Human actions that the history records

1. Publishing was deferred, then resumed: `dx-ball/fa88b84:AGENTS.md:36` "- Commit locally; pushes are deferred until the user asks to resume publishing." and `dx-ball/4d20383:AGENTS.md:37` "The user resumed publishing; keep private originals/tools/evidence untracked."
2. A stop with a handoff: `dx-ball/3f46376:docs/agent/HANDOFF.md:4` "The user requested this handoff and stopped the current reconstruction run."
3. An authorization that ended a block: `f41365c` "gpt-6.1-sol: Authorize bounded source-candidate searches"
4. A stop that cleared the goal: `dx-ball/794b07e:docs/agent/HANDOFF.md:3` "Updated October 21, 2026. The user stopped and cleared the reconstruction goal,"
5. A resume 22 minutes later: `dx-ball/f823bde:AGENTS.md:18` "October21 resumed status: the user explicitly resumed all270 authored exact"
6. A stop of long tests: `dx-ball/docs/agent/HANDOFF.md:42` "sampling were stopped by the user; do not restart them automatically. Never"

### The block of 2026-10-17

- The agent wrote that it was blocked: `dx-ball/54d3d89:docs/agent/HANDOFF.md:107` "Continuation is currently blocked on missing producer evidence. Three consecutive"
- It set its own resume condition: `dx-ball/54d3d89:docs/agent/HANDOFF.md:111` "Resume when target-linked declarations, build context or another independently"
- It kept working. 135 commits lie between the block note and the authorization (Computed: `git rev-list --count 54d3d89..f41365c` prints 136). 26 of their subjects start with "close". The ledger stayed at 393 to 396 rows.
- The authorization came 94.8 hours after the block note (Computed). After it, the count of authored exact functions went from 249 (body of `f08ec86` "gpt-6.1-sol: Record same-run field selection and unchanged COFF") to 270 in 26.5 hours.
- Cause: the policy text and the commit order are evidence that the authorization lifted a limit that the agent had set on its own searches. That it was the only cause is a guess, because the later commits also use new tactics.
- The agent then wrote the rules of section 2 so that it would not block on the same question again: `6151e78` "gpt-6.1-sol: Clarify standing reconstruction authority" and `47142bf` "gpt-6.1-sol: Keep reconstruction execution proportionate"

### Resume and recovery

- Resume rule: `dx-ball/3f46376:docs/agent/HANDOFF.md:46` "If the thread still has a registered goal, resume it. Otherwise start a new"
- Keep the goal: `dx-ball/3f46376:docs/agent/HANDOFF.md:26` "- Keep the full goal across turns and handoffs. A small checkpoint, compatibility"
- Make progress each turn: `dx-ball/3f46376:docs/agent/HANDOFF.md:29` "- Make concrete progress: select a missing operation, ABI, expression or lifetime"
- The handoff file is the only resume state in git. It changed in 545 commits. It grew to 843 lines, then to 1,430, and was cut by hand to 115 lines in `794b07e` "gpt-6.1-sol: Prepare clean handoff and preserve pending wait proof" (Computed).
- A failed helper does not restart the compiler: `dx-ball/docs/agent/SOURCE_CANDIDATE_SEARCH.md:148` "that output. Do not recompile an unchanged digest merely to fix bookkeeping."
- A failed candidate is kept with its real difference count: `dx-ball/config/match-units.toml:3` "# for reviewed nonmatching emissions. --include-candidates"
- A failed analysis session ends. It is not hidden by a larger limit: `dx-ball/docs/agent/REA.md:91` "terminate the session. Do not increase memory ceilings to conceal the failure."
- No subject has revert, retract, reopen, rollback, undo or blocked (Computed). A failure is a new commit.
- No retry cap, no backoff rule and no rule that stops after N failures exists in the instruction files (Computed: `rg -n -i 'retry|backoff|unattended|overnight|max.attempts' AGENTS.md docs/agent` finds no rule).

## 8. Weak or unproven

1. No proof of an unattended run. The repo has no session log, prompt history or token count.
2. A permission question stalled real progress for about four days.
3. Acceptance rows have no writer script and no tie to a compare run.
4. CI cannot run a match, and no hook gates a commit.
5. Resume state is free text that needed six hand cuts (Computed from the six commits whose subjects say consolidate, condense or organize the handoff).
6. Evidence IDs point into untracked files.
7. The docs disagree with the locks in places: `dx-ball/docs/REA.md:48` "This repository uses REA 6.4.0 with Ghidra 12.1.4 through `scripts/rea`." against `dx-ball/config/rea.lock.json:2` "6.5.0"
8. The design is for one session, one CPU and one writer. It has no subagents and no parallel work.

## 9. What to take for this repo

Each line names the dx-ball mechanism and what [10-overnight-design.md](10-overnight-design.md) does with it.

| dx-ball mechanism | Verdict | Reason |
| --- | --- | --- |
| One goal prompt, plus a handoff, plus `AGENTS.md` | Take, with a generated state file in place of free text | The handoff grew to 1,430 lines. This repo already generates session state (ADR-0021) |
| Standing authorization text | Take, and put it in the first prompt | dx-ball got it only after four days of little progress |
| Negative result as a commit ("close") | Take as a `parked` row plus a finding | This repo already has `parked` and `docs/FINDINGS.md` |
| One-command compare with an exit code | Already here | `bodecomp.match --check` |
| Hash-bound acceptance rows | Already better here | `config/functions.csv` is written by `bodecomp.match`, not by hand, and `--check` recompiles |
| Fail-closed target marker | Partly here | `setup_inputs` checks the hash of the XBE, and `sync check` writes a stamp. Add a pre-flight step that fails the run when either is off |
| Explicit demotion | Already here | `bodecomp.match --check` fails when a matched function no longer matches |
| Batch before compare | Already here | A matcher batch is 20 functions |
| Per-file compiler flags | Not now | Issue #46 holds this decision for a human |
| No time limit, no budget, no hook | Do not take | The overnight run has a time limit and a stall line (R2) and one more hook line (R9). It has no cost limit: `/goal` has none, and `--max-budget-usd` works in print mode only |
| Optional reviewer | Do not take | ADR-0013 records a match that passed the byte check with hand-written compiler code, and only a second agent caught it |
