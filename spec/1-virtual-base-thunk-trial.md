Source issue: [#1 Match the virtual-base thunks through real class declarations (M5 trial)](https://github.com/julian-perge/bustin-out-recomp/issues/1)

# Spec: Virtual-base thunk trial, V1

Commands, repo structure and code style are in [AGENTS.md](../AGENTS.md). This spec adds only what the trial needs.

## Objective

652 units in `default.xbe` are this-adjusting thunks for a virtual base. VC71 generates them, so they match only when the real classes are declared (ADR-0013). The trial declares three classes of one virtual-base family for real, lets VC71 emit their thunks, and then runs one matcher batch on code that uses the same bases.

The trial answers one question for the maintainer: does a recovered class make other functions cheaper to match? The answer decides whether class recovery becomes a milestone.

The design decisions are in the issue's comment of 2026-11-14. This spec does not change them.

## Facts from Ghidra (ghidra-mcp, 2026-11-14)

Each class is `class X : public UnkTargetBase, public virtual Unk802A2AC0` in the GameCube donor's terms. Each has a main vtable, a 3-slot vtable for the virtual base, and a vbtable. The base part is 0x44 bytes, so the vbtable pointer is at +0x44.

| | Class 1 | Class 2 | Class 3 (pause screen) |
|---|---|---|---|
| GameCube donor | `Unk8003AA6C` | `Unk80026864` | none (F-0043) |
| Constructor | 0x00047D20 (404) | 0x0003B940 (649) | 0x000A80B0 (193) |
| Destructor | 0x000474C0 (41) | 0x0003B230 (143) | 0x000ACA40 (140) |
| Deleting destructor, slot 0 | 0x00047ED0 (40) | 0x0003B360 (40) | 0x000ACB50 (40) |
| Main vtable | 0x002E3A78, 17 slots | 0x002E3940, 18 slots | 0x002E7578, 19 slots |
| Virtual-base vtable | 0x002E3A68 | 0x002E3930 | 0x002E7568 |
| Virtual base at | +0xEC | +0x1EC | +0x25AC |
| Thunk for slot 0 (14 bytes) | 0x00047CE0 | 0x0003B2D0 | 0x000ACA10 |
| Thunks (8 bytes each) | 0x00047CF0, 0x00047D00 | 0x0003B2E0, 0x0003B2F0 | 0x000ACA20, 0x000ACA30 |
| Thunk targets | 0x00047520 (23), 0x00047D10 (3) | 0x00036670 (306), 0x0003B300 (3) | 0x000A8180 (148), 0x000A8220 (148) |
| Other overridden slots | 1: 0x00047540 (1231), 2: 0x00047A10 (259) | 1: 0x0003C620, 2: 0x0003B2C0 (3), 3: 0x00036570 (56), 6: 0x00038D00 (569), 17: 0x000365B0 (29) | 18: 0x000A8C40 (124), and six large slots (see R3) |

Sizes in brackets are Ghidra function sizes in bytes. The unit's bytes decide a match (F-0075).

Four facts differ from the issue text or add to it:

1. The issue lists the third pair as constructor 0x000ACA40 and destructor 0x000A80B0. It is the reverse. 0x000A80B0 takes the most-derived flag, stores the vbtable 0x002E75C4 and builds the virtual base. 0x000ACA40 is called from slot 0 (0x000ACB50). The class is the pause screen of F-0043, and it holds the buy menu and the build menu as members (F-0041).
2. Each class has one 14-byte thunk: `sub ecx,[ecx-4]`, `sub ecx,<offset of the virtual base>`, `jmp <deleting destructor>`. It is in scope, because it is one of the class's thunks. The 14-byte form at 0x001E3560 (`add ecx,...`) stays out of scope.
3. Slot 1 of class 2, 0x0003C620, is code with no Ghidra function. Its only reference is the vtable entry at 0x002E3944. It has no target unit.
4. All three constructors start with an exception-handling frame (`push -1`, `push <handler>`). The largest function matched by hand so far is 24 bytes, so `bodecomp.match` has never checked a function with such a frame.

The virtual base's own vtable is 0x002E38F4. 18 functions reference it, among them the per-player screens 0x00053DD0 and 0x000BD710.

## Requirements

### R1. `bodecomp.match` checks and records compiler-generated functions

- A thunk has no definition in the source, so no address comment can sit before it. The check reaches it from the class's vtable: the vtable slot's relocation names the thunk, and the thunk is a COMDAT in the object of the class's source.
- The check compares the thunk's bytes and its jump relocation with the original at the address the slot expects. This is the rule that already applies to `??_G` (F-0080).
- A source claims each compiler-generated function it expects, by address, so that `bodecomp.match.scan` sees the claim (ADR-0012). The plan decides the claim's syntax. It chose `// generated: 0xADDRESS`.
- `config/functions.csv` gets one row per claimed compiler-generated function. The status is `matched` only when the bytes and relocations are equal. For a thunk, the function its jump names must also be `matched` in the same run. A claim that the check never reached is an `error`.
- Existing sources without such claims keep their results.
- If the check cannot follow a constructor's exception-handling handler and tables, the same rule is added for them: compare bytes and relocations at the expected address. A probe on class 1's constructor comes before any class work.
- A constructor or destructor that is declared and not matched cannot take a `FUN_` name, so a call to it does not resolve. A line `// declared: 0xADDRESS Class::Class` (or `Class::~Class`) in a source, or in a header it includes, gives it its address. The line takes only constructors and destructors, and it is not a claim (plan, 2026-11-14).

### R2. One shared header for the two bases

- `src/game/auto/UnkTargetBase.h` declares `UnkTargetBase` and `Unk802A2AC0` once. The three class sources and the callers batch include it. `bodecomp.cl` has no include path, so the header sits beside the sources.
- The declarations give the real layout and every virtual function in slot order. Functions that are not matched are declared under their `config/symbols.txt` names (`FUN_XXXXXXXX`), so the match resolves them. Constructors and destructors take a `declared` line (R1).
- Each derived class is declared in its own source file, not in a header.

### R3. Three classes, each in one source file

Order: class 1, class 2, class 3. Each class is one matcher run and one reviewer run, as in `docs/WORKFLOW.md`, "Matching". Default flags (ADR-0004).

| Class | Source | Required functions |
|---|---|---|
| 1 | `src/game/auto/00047D20.cpp` | 10: constructor, destructor, deleting destructor, three thunks, 0x00047520, 0x00047D10, 0x00047540, 0x00047A10 |
| 2 | `src/game/auto/0003B940.cpp` | 13: constructor, destructor, deleting destructor, three thunks, 0x00036670, 0x0003B300, 0x0003C620, 0x0003B2C0, 0x00036570, 0x00038D00, 0x000365B0 |
| 3 | `src/game/auto/000A80B0.cpp` | 9: constructor, destructor, deleting destructor, three thunks, 0x000A8180, 0x000A8220, 0x000A8C40 |

- Every other member function is declared, so the class layout is real. A match of one is reported as extra and is not required.
- Class 3 declares its six large slots and does not require them: UpdatePause 0x000A8720 (1229), 0x000ADA10 (345), HandlePauseMessage 0x000A8CC0 (2814), SetPauseVariable 0x000A9CF0 (4553), GetPauseVariable 0x000AAEC0 (5041), InitPauseMenu 0x000A82C0 (1105).
- Class 3 needs declarations of its two member classes (F-0041) with their real sizes, constructors and destructors.
- `src/game/trivial/` claims three of the required functions today with placeholder sources: 0x00047D10, 0x0003B300 and 0x0003B2C0. Three more trivial claims lie inside class 1's address range (0x00047B20, 0x00047CD0, 0x00047EC0), and the plan checks whether they belong to the class. After a class source claims a function, `uv run python -m bodecomp.trivial generate` drops the placeholder (ADR-0012).
- Names are placeholders. A class with a donor takes the donor's class name. The pause screen is `S_000A80B0`. Matched functions keep their `auto` names (ADR-0011).

### R4. One callers batch

- 20 functions, the M4 batch size, so the cost compares with batch 3.
- The batch holds 0x00053DD0 and 0x000BD710. The plan picks the other 18: functions that reference vtable 0x002E38F4 or call the base constructor 0x001249C0 or destructor 0x001248B0, smallest first, at least 17 bytes, not claimed.
- The plan lists the 47 vtable-store functions that the third gen_trivial pass did not keep (F-0080) and marks the ones whose class uses a shared base. Those are tried with the shared header, in the batch or beside it.
- Code that VC71 generates is left out of the selection (ADR-0013): unwind funclets, deleting destructors and vbase destructors. The picked functions are in issue #9.
- The matcher gets the shared header and the three class sources.

### R5. Results file

`docs/thunk-trial-results.md` holds:

- One row per batch (class 1, class 2, class 3, callers): given, matched, nonmatching, parked, total tokens (matcher plus reviewer), tokens per matched function, next to batch 3's 7,557.
- Matched bytes and tokens per matched byte for each batch, next to batch 3's 445 (18 matched functions of 17 bytes, 136,027 tokens). Batch 3 was 20 functions of 17 bytes each and the callers batch is 2,278 bytes, so tokens per function alone do not compare (plan, 2026-11-14).
- The tokens of the R1 tool work, in their own row.
- The reviewer's verdict per batch.
- The trial's outcome, one of: pass, no gain, stopped, class parked.
- New findings go to `docs/FINDINGS.md` through the lead.

### R6. Stop rule

- No token cap. Tokens are reported and stop nothing.
- After each class, the lead names the blocker of every function that is not `matched`.
- A blocker that the remaining classes share stops the trial: the remaining classes and the callers batch do not run, and the results file says `stopped`. "Shared" needs evidence: a Ghidra reference or a test compile that shows the same construct in a remaining class.
- A blocker that belongs to one class parks that class. The trial goes on.

## Outcomes

| Outcome | Condition | What follows |
|---|---|---|
| Pass | All three classes whole, and the callers batch costs less than 7,557 tokens per matched function or matches at least one of the 47 | The case for a class-recovery milestone is made. A new issue proposes it. |
| No gain | All three classes whole, the callers batch shows neither | The thunks wait. A class is declared only when a matcher batch needs it. The search for the next byte shape among larger functions goes ahead. |
| Stopped | A shared blocker | The blocker becomes a finding. The thunks wait. |
| Class parked | One or two classes parked on their own blockers | The results file reports it. The maintainer decides. |

## Prerequisites

1. The repo overhaul's first push. A Build stage opens a pull request, and nothing is pushed yet.
2. The delinker check for v0.9.3: `uv run python -m bodecomp.unitsplit --compare <folder>` reports 0 objects differ (`docs/WORKFLOW.md`). It comes before the next `tools/delink.sh`.
3. 0x0003C620 becomes a Ghidra function and gets a target unit: `tools/create-functions.sh`, `sync export`, `tools/delink.sh`, and the re-link gate with 0, 0 and 0 (ADR-0006). Only class 2 needs this.
4. 0x0021F734 becomes a Ghidra function and takes the name `__purecall` from `bodecomp.libmatch`. Ghidra shows the pure-virtual-call handler's code there, with 1,785 references and no function, and slots 1 and 2 of vtable 0x002E38F4 point at it. All three classes need it. It is created in the same run as 0x0003C620 (issue #2).

## Tech stack

VC71 `CL.Exe` under wibo with `/O2 /G7 /arch:SSE /GX` (ADR-0004, ADR-0017). Python with uv. Ghidra 12.2 through ghidra-mcp, read-only for matcher and reviewer (ADR-0003).

## Commands

See [AGENTS.md](../AGENTS.md), "Every task" and "Commands". The ones this spec uses most:

```
uv run python -m bodecomp.match            # compile every source, write config/functions.csv
uv run python -m bodecomp.match --check    # fail unless every claimed function is matched
uv run python -m bodecomp.trivial generate # drop placeholders that a class source now claims
uv run pytest -q && uv run ruff check . && uv run python -m bodecomp.findings check && uv run python -m bodecomp.match --check
```

## Project structure

```
bodecomp/match.py                 R1
tests/test_match.py               R1 tests
src/game/auto/UnkTargetBase.h     R2
src/game/auto/00047D20.cpp        class 1
src/game/auto/0003B940.cpp        class 2
src/game/auto/000A80B0.cpp        class 3
src/game/auto/                    callers batch sources
docs/thunk-trial-results.md       R5
```

## Code style

The shape of a class source. Signatures here are examples, not facts.

```cpp
#include "UnkTargetBase.h"

class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    Unk8003AA6C(int player);
    virtual ~Unk8003AA6C();
    virtual void FUN_00047540();
    virtual void FUN_00047520(int mode);
};

// 0x000474C0
Unk8003AA6C::~Unk8003AA6C()
{
}
```

The source holds no vtable store, thunk, exception-handling frame, deleting destructor, or call to a base or member constructor or destructor. The declarations make the compiler emit them (ADR-0013).

## Testing strategy

- R1 is built test first in `tests/test_match.py`, with synthetic COFF objects like the `??_G` test. Cases: a thunk with equal bytes and a matched target is `matched`. One different byte is `nonmatching`. A thunk whose target is `nonmatching` is not `matched`. A claim the check never reached is an `error`. A source with no claims gives the rows it gave before.
- A class is verified by `bodecomp.match --check` and by its rows in `config/functions.csv`.
- A reviewer pass per batch checks the sources against ADR-0013 and compiles the other form for each claim about compiler behavior.
- The full gate of AGENTS.md runs before each commit.

## Boundaries

- Always: use ghidra-mcp for facts about the binary (ADR-0003). Record the token counts of a batch when it ends. Send proposed findings to the lead.
- Ask first: other compiler flags for a class file (per-file flags do not exist, F-0021). A change to `tools/delink.sh` or the export scripts. Any push.
- Never: write by hand what VC71 generates. Weaken the check to get a match. Add a token cap or change the stop rule. Write to Ghidra from a matcher or reviewer.

## Success criteria

1. `uv run pytest -q` passes with the R1 cases above.
2. For each class, `config/functions.csv` lists every required address of R3 as `matched` from that class's source file, and `bodecomp.match --check` passes.
3. No required function is claimed by a file in `src/game/trivial/`.
4. The reviewer pass of each class and of the callers batch is clean.
5. The matched count of functions outside the trial does not fall.
6. `docs/thunk-trial-results.md` has the rows and the outcome of R5.
7. When the trial stops early, criteria 2 to 4 apply only to the classes that ran, and the results file names the shared blocker with its evidence.

## Out of scope (deferred)

- The 14-byte thunk form at 0x001E3560 and the other 643 thunks: they wait for the trial's outcome.
- Real names for the classes: no string or donor states them.
- The six large pause-screen slots and the non-virtual members of class 2: declared only.
- Headers for the derived classes.
- Per-file compiler flags.
- The milestone numbering: the overhaul spec owns it.
- The search for the next byte shape among larger functions: it follows the outcome.

## Risks

- Size. The required functions reach 1,231 bytes (class 1), 649 (class 2) and 193 (class 3). The largest hand-matched function is 24 bytes. A function that does not match after five attempts parks its class.
- Exception handling. If VC71's handler and tables do not compare equal for class 1's constructor, the same holds for all three, which is a shared blocker.
- Thunk emission. The earlier test compile gave the 8-byte form. The 14-byte destructor thunk is not yet reproduced.
- Member function pointers. Class 1 stores a table of them, and their size depends on the class's inheritance model.

## Open questions

None. The maintainer approved the spec on 2026-11-14, which settles the three questions it asked:

1. The results file is `docs/thunk-trial-results.md`.
2. Exception-handling support in `bodecomp.match` is part of R1 when the probe shows it is missing.
3. For the outcome "class parked", the maintainer decides after the results.

The plan of 2026-11-14 added the `declared` line and the claim syntax in R1, the exclusion in R4, the bytes columns in R5 and prerequisite 4. The maintainer approved each in the plan session. The tasks are sub-issues #2 to #10 of the source issue.
