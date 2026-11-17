# Workflow

How to run the tools without rediscovering them. The method is in `docs/METHODOLOGY.md`; decisions are in `docs/adr/`; facts are in `docs/FINDINGS.md`.

## The ghidra-mcp server

- Start: `tools/ghidra-mcp-headless.sh` (port 8089, project `ghidra/BustinOut.gpr`). Check it with `curl -s http://127.0.0.1:8089/check_connection`.
- Stop: `pkill -f '[G]hidraMCPHeadlessServer'`. The brackets keep the pattern from matching the shell that runs `pkill`: in a Claude Code Bash call, the plain pattern also stops that shell.
- Writers: only the lead session or one `namer` agent. A task that changes the Ghidra project has the `ghidra-writer` label, and its assignee is the lock. At most one open task with the label is assigned. The hook prints it, and `namer` and `reviewer` query it with `gh issue list --label ghidra-writer --state open --assignee '*'` (ADR-0003, ADR-0021).
- A Ghidra-writer task may change only what a tracked text file records. It commits `config/symbols.txt` after `sync export`. Any other change in Ghidra is scratch and is lost on a rebuild (ADR-0002, ADR-0021). The task does not count that change as done.
- `matcher` and `reviewer` have only read-only ghidra-mcp tools, and their instructions forbid the Bash routes that still write (F-0025).
- `.mcp.json` is per machine. It is untracked and git-ignored, because it names the path to `uv`, which differs between machines. Create it on each machine with the content below, and put the output of `command -v uv` in `command`. The bridge starts with `--no-lazy`, so every tool group is registered when it connects. A group loaded later with `load_tool_group` never reaches a subagent that is already running (F-0023). Use `search_tools` with keywords to find a tool.

  ```json
  {
    "mcpServers": {
      "ghidra-mcp": {
        "type": "stdio",
        "command": "<output of command -v uv>",
        "args": ["run", "--directory", "${HOME}/git/bethington/ghidra-mcp", "bridge-mcp-ghidra", "--transport", "stdio", "--no-lazy"],
        "env": {"GHIDRA_MCP_URL": "http://127.0.0.1:8089"}
      }
    }
  }
  ```
- The scripts that run Ghidra source `tools/env.sh`, which sets `GHIDRA_HOME`. An existing `GHIDRA_HOME` wins. Otherwise it uses the newest `Cellar/ghidra/<version>/libexec` under `brew --prefix` (`$HOMEBREW_PREFIX`, then `/opt/homebrew`, when `brew` is not on `PATH`). When none holds `support/analyzeHeadless`, it prints the paths it tried and exits 1.
- The headless server opens no program. Pass `program="default.xbe"` to every ghidra-mcp tool call (F-0024).
- `apply_data_type` clears the range unless `clear_existing` is false (F-0011).
- After a ghidra-mcp update, refresh the read-only tool list: `uv run python -m bodecomp.agent_tools`.

## The decompile tree

`build/decomp-tree` holds Ghidra's decompiled C of every function as files, so a question across many functions is one `rg` call and not one `force_decompile` call per function. One `force_decompile` call takes 0.25 to 0.33 s, because the server opens a new decompiler for each call. The sweep keeps one decompiler open and wrote all 21,194 functions in 671 s (issue #87).

- The lead runs `tools/decomp-tree.sh` with the server up: once per machine, and again after each `tools/rebuild-ghidra.sh`. It creates or adopts the tree. A new tree, or one whose last sweep did not finish, gets a full sweep (about 11 minutes). For a tree that was swept before, the server decompiles again only the functions that changed. The script waits until the tree matches the program. While the server runs, the tree follows renames and other program changes by itself.
- Search it with the path named, `rg <pattern> build/decomp-tree`: `build/` is git-ignored, so `rg` from the repo root without the path skips it. `index/by-address.tsv` gives the file of each function. `STATUS.md` gives the state; `state: clean` means the tree matches the program.
- A hit in the tree is an index, not evidence. Before a report or finding states a fact, confirm it with a ghidra-mcp tool, and the Checked line names that tool (ADR-0003). When the tree is missing or `STATUS.md` does not say `state: clean`, use ghidra-mcp only.

## Rebuilding the Ghidra project from text

1. With the server running, `uv run python -m bodecomp.sync export`, then commit `config/symbols.txt`.
2. Stop the server, then `tools/rebuild-ghidra.sh`. It refuses to run while the server is up or `symbols.txt` is uncommitted. After the import it runs `tools/create-functions.sh` over every function start in `symbols.txt`, so functions that the import's analysis misses are created again, and it fails if any listed start does not end up as a function start.
3. Start the server, open the program (`curl -s -X POST http://127.0.0.1:8089/open_program -H 'Content-Type: application/json' -d '{"path": "/default.xbe", "auto_analyze": false}'`), then `uv run python -m bodecomp.sync apply` and `uv run python -m bodecomp.sync check`. Expect 0 differences both ways. With 0 differences, `sync check` writes `ghidra/.sync-stamp`: the SHA-256 of `config/symbols.txt` and the SHA-256 of the address and kind columns of its `function` lines. No other command writes it, and a check with a difference leaves it unchanged (ADR-0021, ADR-0022). The session-start hook compares the stamp with `config/symbols.txt` and prints one `ghidra project:` line: level, no stamp, function starts changed (rebuild), or names changed (`sync apply`, then `sync check`). A function rename or size change counts as names changed.

## Delink and re-link

- `tools/delink.sh` writes `build/target/text.obj`, the delinker tables `build/target/relocs.tsv` and `build/target/symbols.tsv`, and one object per unit to `build/target/units/` (ADR-0006). Stop the server first; both open the same project.
- Run `uv run python -m bodecomp.split` before each delink. `tools/delink.sh` cuts the units that `build/target/units.txt` lists and does not write that file, so a list from before a change to the function starts in `config/symbols.txt` gives wrong units, and the re-link gate does not notice (F-0085).
- After a delinker update, check the split against the delinker itself: run `ExportUnits.java` headless on a copy of the project into a folder, then `uv run python -m bodecomp.unitsplit --compare <folder>`. It must report 0 objects differ.
- `uv run python -m bodecomp.relink` must report 0 mismatched bytes, 0 unresolved names and 0 unit problems (ADR-0006).

## Function discovery

Code that no Ghidra function covers is invisible to the units and to the namer (F-0016, F-0026). With the server stopped:

1. `uv run python -m bodecomp.gaps report` prints the gaps in `.text` (bytes that no function in `symbols.txt` covers) and how many of their bytes are not `0xCC` padding.
2. `uv run python -m bodecomp.gaps candidates` writes `build/target/candidates.txt`: each 16-byte-aligned address in a gap whose previous byte is padding and whose own byte is not. The list is preliminary; it comes from raw bytes.
3. `tools/create-functions.sh` first disassembles the candidates from the lowest address up, then creates the functions from the highest address down and runs auto-analysis on the changes. It rejects data, an address inside an instruction of lower code (`mid-instruction`: a `0xCC` operand byte looks like padding), a new function that the instruction before it falls through to (`falls-through`: a `0xCC` that ends an SSE instruction), bytes that do not disassemble, and addresses Ghidra will not make a function; an address that analysis turns into a function start afterwards is not counted. The reasons are in `build/create-functions-rejected.txt`; a `bad-instruction` line also names the first address where disassembly failed, which counts an error mark that was already there when the flow reaches that address and finds no instruction. Instructions outside functions that conflict with a candidate (Ghidra's analysis disassembles from constants that look like addresses) are cleared and not restored, even when the candidate is rejected.
4. Start the server, open the program, then `uv run python -m bodecomp.sync export` and commit `config/symbols.txt`; the rebuild recreates these functions from it. `sync export` keeps a named data entry that Ghidra does not list, because Ghidra lists a label only on defined data (F-0010); a function Ghidra no longer has is dropped.

## SDK names

- `uv run python -m bodecomp.libmatch` renames SDK functions from the stamped XDK libraries (ADR-0005). Reruns are idempotent (F-0012). Run `sync apply` afterwards to push the names into Ghidra.

## String names

Game functions are named from the strings they reference (ADR-0008). With the server stopped, `tools/export-strings.sh` writes `build/strings.tsv`; export it again after functions change.

1. `uv run python -m bodecomp.names stated` names functions whose own string states `Class::Method()`.
2. `uv run python -m bodecomp.names batch N` lists batch N: each game function with strings, its current name and tier, and its strings with their addresses. The batches are numbered over all such functions, named or not, so batch N stays the same.
3. A namer records a name with `uv run python -m bodecomp.names set 0xADDRESS NAME string:0xSTRING[,0xSTRING]`, or removes one with `names clear 0xADDRESS`. Never rename a game function in Ghidra directly: `sync export` stops on such names.
4. After a batch, with the server up and `default.xbe` open (see "The ghidra-mcp server"): `uv run python -m bodecomp.sync apply`, then `sync check` (0 differences) and `names check` (0 problems).

Rules for a name:

- Name a function only when its strings, together with what its code does with them, say what it does. A format string (`%d`), a common word (`true`, `select`) or a key read in a long list is not enough alone.
- Use `Class::Method` only when a string the function references states that the function is a member of the class, for example `CreateASimBaseState::Update()`. A class name on its own or an "X operator new" tag does not (F-0033). Otherwise use a flat CamelCase verb and object: `LoadLightingTweaks`, `GetDialogVariable`.
- When no string states a screen class's name, its flat names may take a label from the class's Flash calls or variable prefix, such as HUD from `showHUD` and `hud_` (F-0039, F-0042). Record the label in a finding.
- Name screen vtable slots alike: slot 1 `Update<X>`, slot 2 `Draw<X>`, slot 6 `Handle<X>Message`, slot 7 `Set<X>Variable`, slot 8 `Get<X>Variable`, slot 12 `Get<X>Name` (F-0036, F-0044).
- Name an in-place constructor (it installs the vtable and returns `this` without allocating) `Construct<X>`, and a non-deleting destructor `Destroy<X>`. `Create<X>` means a function that allocates and then constructs, as `CreateERRleTexture` does.
- A source path such as `.\ObjectSim.cpp` names a file, not a function. Report it; do not build a name from it alone.
- An MSVC initializer for one global (it constructs the global and registers its destructor with `_atexit`) is named `DynamicInit_<Global>`, for example `DynamicInit_LightingTweaks`.
- A class-record initializer in 0x2409C0..0x242B40 (it calls 0x1550C0 and stores the returned record in a global, with no `_atexit`) is named `DynamicInit_<X>Class` while that global has no name, for example `DynamicInit_ESimClass` (F-0034).
- Cite only strings that support the name, by the addresses `names batch` prints.
- Some four-byte "strings" in `build/strings.tsv` are float constants, such as "33s?" for 0.95f (F-0038). They support no name.
- Spell an abbreviation as the string that supports the name spells it: `ShowCAS` after "showCAS", `LoadCasAnimationList` after "CasAnimationList".

## Matching

`uv run python -m bodecomp.match` compiles every `src/**/*.cpp` except `src/m0` with VC71 at the default flags `/O2 /G7 /arch:SSE /GX` (ADR-0004, ADR-0017), compares each function with its target unit in `build/target/units/`, prints one line per function and writes `config/functions.csv`. `--check` fails when the CSV is stale. `uv run python -m bodecomp.match candidates N` lists N unlisted game functions (not `sdk`), fewest relocations first, then smallest; `--min-size` (default 16) skips smaller units, and `--min-relocs` skips units with fewer relocations.

A source function is paired with its target by an address comment on the line before its definition. A parked function adds its blocker class on the next line:

    // 0x0012F3A0
    // parked: scheduling
    void ESimsApp::Update()

The definition may be `operator new` or `operator delete`, free or in a class; other operators are not read. A vtordisp thunk that VC71 names after the function is not taken as its definition.

A constructor or destructor that is declared and not matched cannot take a `FUN_` name. An override that is declared and not matched cannot take its own `FUN_` name either: it keeps the name of the base's slot, and that name gives the base function's address. A `declared` line gives such a function its address:

    // declared: 0x001249C0 UnkTargetBase::UnkTargetBase
    // declared: 0x001248B0 UnkTargetBase::~UnkTargetBase
    // declared: 0x000A8720 S_000A80B0::FUN_00124940

The line sits in a source, or in a header that the source includes with `#include "..."`. A header's own quoted includes are read too, each from the folder of the file that includes it. The line is for a constructor, a destructor or an override. The tool checks only that the name is a member function, so other member functions keep their `FUN_` names by rule and not by a check. It is not a claim: the address gets no row in `config/functions.csv`, and two files can hold the same line. A line for a free function or an operator, a line without an 8-digit address, and one name with two addresses are problems that stop the run. All constructors of a class share one name, so a class with two constructors that are not matched cannot declare both. For the same reason, one line gives its address to every overload of a member function.

A thunk or a deleting destructor has no definition in the source, so no address comment can sit before it. A `generated` line claims one:

    // generated: 0x00047CE0

The line sits anywhere in a source, with one address per line. It is a claim, as an address comment is. The address gets a row in `config/functions.csv`, and `bodecomp.trivial generate` writes no source for it. An address with two claims is a problem that stops the run, and so is a line without exactly one 8-digit address. A header takes no `generated` line, because only the sources are read for claims.

The check does not look for a claimed function by name. A function with an address comment in the same source leads to it, through the rule for compiler-generated code below. For a thunk, a destructor stores the class's vtable, the relocation of the vtable slot names the thunk, and the original slot gives the thunk's address. The row follows the checks that reached the function:

- `matched`: a check that reached the function passed, so its bytes and relocations equal the original's at the claimed address.
- `nonmatching`: every check that reached the function failed. The detail is the problem of the first one. One check compares many items and fails as a whole, so the problem can be in another item. A byte difference names that item's address, and a relocation that points elsewhere names its section and offset in the built object.
- `error`: no check reached a compiler-generated function at the address.

A claimed function that ends in a jump (`E9` and a REL32 relocation in its last five bytes) is a thunk. A thunk is `matched` only when the function it jumps to has a `matched` row in the same run. The rule follows a chain of jumps to its end. That function needs its own claim: an address comment, or a `generated` line for a deleting destructor. Exception-handling funclets and handlers take no claim and get no row. They are checked as part of their function.

A function matches when the built bytes equal the unit's bytes outside relocation sites, the unit has only `0xCC` or `0x90` padding past the built length, both sides have relocations of the same type (DIR32 or REL32) at the same offsets, and each site resolves to the same address plus addend on both sides. The built side resolves a symbol as follows. A function in the same object counts as the address in its address comment. Data in the same object, such as a string literal or a vtable, counts as its target address only when its bytes equal the XBE bytes there and its own relocations point where the XBE pointers do. A weak external, such as the `??_E` vector deleting destructor in a vtable, counts as the symbol it stands for. Code with no address comment is code the compiler generated, such as a scalar deleting destructor, and counts as the address the original relocation points to only when its bytes and relocations equal the original's there. When one relocation's chain reaches the same item twice, both references must expect the same address. A relocation of an item that points elsewhere does not end the comparison of the item's other relocations, so every item that the chain can reach is compared. An exception-handling frame is checked through the same rule: the handler that the function pushes, the function info it loads, the unwind table and each unwind funclet are compared with the original at the addresses the chain gives. In code, an item runs to the next function symbol, so a label inside a funclet does not end it. `__except_list` counts as 0, the absolute value that `libcmt.lib` gives it, because the original has a plain 0 and no relocation there. An external constructor or destructor with a `declared` line counts as that line's address. An external `FUN_`, `DAT_` or `LAB_` name gives its address, and any other external name must name exactly one entry of `config/symbols.txt`, by its exact name or its scope path (`?B@A@@...` is `A::B`). Anything else is `nonmatching`, with the share of equal bytes and the first difference. The tests in `tests/test_match.py` include deliberately wrong functions for each rule.

A batch is 20 functions from `match candidates 20 --min-size 17`; smaller functions are left to `bodecomp.trivial`. After each merge the lead adds a row to the batch table in `docs/m4-results.md`.

1. The lead picks the functions with `match candidates`, creates a worktree and gives them to one `matcher`.
2. The matcher writes the sources and runs `bodecomp.match` until each function is `matched`, or parked after five honest attempts.
3. A `reviewer` reruns `bodecomp.match` in the worktree and reads the sources.
4. The lead merges, then runs the full gate: `bodecomp.match --check` with every claimed function `matched`, `pytest`, `ruff check`, and after recording any real names, `sync check` with 0 differences, `names check` with 0 problems, `ledger --check` and `findings check`.

## Trivial functions

`uv run python -m bodecomp.trivial generate` writes C++ for small game functions by their byte shape and keeps only the ones that match. It takes every game function whose unit is 16 bytes or less after padding (`--max-size` changes this) and that no source outside `src/game/trivial/` claims. It recognises a fixed set of shapes, such as an empty function, `return 0`, a member getter, a global read, a forwarding jump, `delete this`, or the empty constructor or destructor of a class with a virtual destructor, and writes them in one scratch file per 64 KiB block of addresses, `build/trivial/<address >> 16>.cpp`. It compiles each scratch file and compares it with `bodecomp.match`. It then replaces `src/game/trivial/` with files that hold only the matched functions, and rewrites `config/functions.csv`. It needs `build/strings.tsv` from `tools/export-strings.sh`, because a function that returns a string's address is written with the string literal when the exported text matches the bytes in the xbe. Before compiling, it drops a function that calls a `FUN_` function defined in the same block, because VC71 would inline the call (F-0073). The sources use placeholder names: `FUN_<address>` for a function, `S_<address>` for the struct of a member function, and `DAT_<address>` for a global. When a scratch file does not compile, the command prints the block and the first compiler error, changes nothing under `src/game/trivial/`, and exits 1. Running it twice gives the same files. When a matcher claims a generated function in another file, `bodecomp.match` reports the address as claimed twice until the next `generate` run, which drops it from `src/game/trivial/`.

`uv run python -m bodecomp.trivial shapes [N]` lists the N most common byte patterns among the small game functions that no source claims, with relocation sites shown as `R`, their counts, and the shape that recognises each pattern or `-`. A pattern with a shape that is still listed did not match. The test `test_every_shape_compiles_to_its_pattern` compiles each shape with VC71 and checks its pattern.

A match from `generate` proves the bytes, not that the source is plausible, and one shape writes hundreds of functions. So before `generate` runs with a new shape, or with a changed source for an existing one, the lead sends the `reviewer` the shape's source for one example address and asks for a pass or fail against the plausibility rule (ADR-0013). A shape that hand-writes code VC71 generates itself, such as a vtable pointer store, fails. The verdict goes in the shape's row in the milestone results file.

## Matched names

A function whose C++ compiles to its original bytes takes the `matched` tier (ADR-0011). Matchers do not write `config/symbols.txt`. A function whose source uses placeholder names (`S_00018390::fn_00018390`) keeps its `auto` name, and only `config/functions.csv` records its match (ADR-0011). The lead records a match only after its function has passed the full gate on `main`, with `uv run python -m bodecomp.names set 0xADDRESS NAME src/PATH.cpp`, where NAME is the VC71 decorated name, or the plain name of a C function. The tool sets the tier from the `src/` evidence. It refuses a source file that does not exist, and an address that `config/functions.csv` does not list as `matched` from that same file. It replaces an `auto`, `gc` or `string` name, and appends ` was:OLDNAME` to the evidence when the old name was not `auto`. `names check` also checks matched entries, including that each source file exists and that `config/functions.csv` still lists the function as `matched` from it. Then run `sync apply` and `sync check` as for string names.

## Answering common questions

Read-only tools, as named in ghidra-mcp 7.0.0. Confirm a name with `check_tools` if a call fails.

- Who references an address: `get_xrefs_to`.
- What an address calls or reads: `get_xrefs_from`.
- A function's code: `disassemble_function` for the instructions, `force_decompile` for C.
- Code outside functions: `find_code_gaps`.
- Strings: `search_strings`, or `list_strings` with a filter. `search_byte_patterns` finds bytes Ghidra has not defined as strings; a hit is preliminary until its references are checked.

## End of a batch

1. `uv run pytest -q`.
2. `uv run python -m bodecomp.ledger`, then `uv run python -m bodecomp.findings check`.
3. Add or update FINDINGS entries from the agents' reports. The Verification section of the pull request gives the command output or the Ghidra reference that shows the state of the batch.

At the end of a plan, also set every unfinished `active` finding back to `open`. Record a decision as an ADR when it is settled (ADR-0014).

## GameCube watch (on request only)

1. Take the last-seen SHA from the newest entry of `docs/gc-donor-watch.md`.
2. `gh api 'repos/daftblazer/bustin-out-decomp/commits?per_page=100'` and stop at that SHA. If nothing is newer, say so and change nothing.
3. `gh api repos/daftblazer/bustin-out-decomp/compare/<last>...<newest>` lists the changed files. Read the non-`src/` changes that matter: `docs/`, `include/`, `config/G4ME69/symbols.txt` and `splits.txt`, `tools/`, `configure.py`, the README progress.
4. Append one dated entry to `docs/gc-donor-watch.md`: the new last-seen SHA, the commit count, the subsystems touched, the progress number, and what could transfer to the Xbox side. Anything about the Xbox binary is preliminary unless checked through ghidra-mcp. A transferable fact also gets a FINDINGS entry.
5. Commit only that file (and FINDINGS if changed).
