# Virtual-base thunk trial results

The trial is issue #1, with the spec `spec/1-virtual-base-thunk-trial.md`. It declares three classes of one virtual-base family for real, lets VC71 emit their thunks, and then runs one matcher batch on code that uses the same bases. This file holds the batch table, the cost of the tool work, the probe that came before the classes, and the outcome (R5 of the spec).

## Outcome

Not decided. No class has run yet. The probe below found no blocker that stops the trial (R6), with one condition: the constructors need `/GX`, which is not a default flag (F-0088).

## Batches

Tokens are the total of the matcher and the reviewer. M4 batch 3 is the comparison: 20 functions of 17 bytes each, from `docs/m4-results.md`.

| Date | Batch | Given | Matched | Nonmatching | Parked | Total tokens | Tokens per matched function | Matched bytes | Tokens per matched byte | Reviewer's verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-10-12 | M4 batch 3 | 20 | 18 | 0 | 2 | 136,027 | 7,557 | 306 | 445 | see `docs/m4-results.md` |
| | Class 1 (issue #6) | 10 | | | | | | | | |
| | Class 2 (issue #7) | 13 | | | | | | | | |
| | Class 3 (issue #8) | 9 | | | | | | | | |
| | Callers (issue #9) | 20 | | | | | | | | |

## Tool work (R1)

| Work | Issues | Tokens |
|---|---|---:|
| `bodecomp.match`: declared lines, the probe, generated claims | #3, #4, #5 | not measured |

The plan left open how the tokens of a lead session are measured, and that is not settled. The build sessions of issues #3 and #4 reported no total. A session's transcript records the usage of each response, so a total can be read from it after the rule is chosen.

## Probe of a class 1 skeleton (issue #4, 2026-11-15)

Two risks would stop the whole trial, so a scratch skeleton of class 1 checked them before any class work. The skeleton is `class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0` with the constructor, the destructor and the four overrides. It is not under `src/`, and its bodies are not match attempts. It went through `bodecomp.match.check_source`.

### Thunks

VC71 emits the three thunks with the original bytes at the default flags `/O2 /G7 /arch:SSE` (F-0087).

| Address | Original | Built | Built jump names |
|---|---|---|---|
| 0x00047CE0 | `2b49fc81e9ec000000e9e2010000`, jump to 0x00047ED0 | `2b49fc81e9ec000000e9` and a REL32 relocation | `??_EUnk8003AA6C@@UAEPAXI@Z`, which stands for the deleting destructor |
| 0x00047CF0 | `2b49fce928f8ffff`, jump to 0x00047520 | `2b49fce9` and a REL32 relocation | the override of slot 1 |
| 0x00047D00 | `2b49fce908000000`, jump to 0x00047D10 | `2b49fce9` and a REL32 relocation | the override of slot 2 |

`check_source` reports the destructor 0x000474C0 and the overrides 0x00047520 and 0x00047D10 as `matched`. The destructor stores both vtables, so its match needs the 17 slots of the main vtable, the three thunks and the deleting destructor 0x00047ED0 to compare equal with the original. The built vbtable is `bcffffffa8000000`, the bytes at 0x002E3AC8.

### Exception-handling chain

At the default flags VC71 emits no exception-handling frame, so the constructor cannot match. With `/GX` added it emits the frame, and the chain compares equal (F-0088).

    flags: /O2 /G7 /arch:SSE
    0x00047D20 nonmatching   1.0  first difference at +0x0, target 404 bytes, built 129 bytes

    flags: /O2 /G7 /arch:SSE /GX
    0x00047D20 nonmatching   7.4  first difference at +0x18, target 404 bytes, built 177 bytes

The first 0x18 bytes are the frame setup: `push -1`, the push of the handler, the read and the write of the exception list, and `sub esp,0xc`. The difference at +0x18 is the skeleton's own body. For the handler site at +0x3 the resolver returns 0x002341CF, the address the original pushes, after it compared these items with the original:

| Original address | Item in the built object |
|---|---|
| 0x002341CF | the handler, `mov eax,<function info>` and a jump to `___CxxFrameHandler` |
| 0x002FA7B8 | the function info, 28 bytes |
| 0x002FA7B0 | the unwind table, one entry |
| 0x002341B0 | the unwind funclet, 31 bytes |
| 0x000359B0 | the destructor of the virtual base, which the funclet jumps to |
| 0x002E38F4 | the vtable of the virtual base |
| 0x000359C0 | the deleting destructor of the virtual base |

Before this task the resolver could not finish that check. `bodecomp.match` got three rules for it (F-0089).

With `/GX` added to the default flags, every claimed source gives the same row as before: 3306 matched, 3 parked, and `config/functions.csv` is equal.
