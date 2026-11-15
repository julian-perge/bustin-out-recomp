# Virtual-base thunk trial results

The trial is issue #1, with the spec `spec/1-virtual-base-thunk-trial.md`. It declares three classes of one virtual-base family for real, lets VC71 emit their thunks, and then runs one matcher batch on code that uses the same bases. This file holds the batch table, the cost of the tool work, the probe that came before the classes, and the outcome (R5 of the spec).

## Outcome

Not decided. Classes 1, 2 and 3 are whole: the 10 required functions of class 1, the 13 of class 2 and the 9 of class 3 are `matched`, and no function has a blocker, so the stop rule (R6) stops nothing. The constructors need `/GX`, and the default flags gained it after the probe (F-0088, ADR-0017). The callers batch matched 18 of its 20 functions at 32,848 tokens per matched function, which is more than batch 3's 7,557. 0x00137AF0, one of the 47 of F-0080, is `matched`, but it is not a vtable store (F-0102). Issue #10 writes the outcome.

## Batches

Tokens are the total of the matcher and the reviewer. M4 batch 3 is the comparison: 20 functions of 17 bytes each, from `docs/m4-results.md`.

| Date | Batch | Given | Matched | Nonmatching | Parked | Total tokens | Tokens per matched function | Matched bytes | Tokens per matched byte | Reviewer's verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-10-12 | M4 batch 3 | 20 | 18 | 0 | 2 | 136,027 | 7,557 | 306 | 445 | see `docs/m4-results.md` |
| 2026-11-15 | Class 1 (issue #6) | 10 | 10 | 0 | 0 | 297,865 | 29,787 | 2,031 | 147 | clean |
| 2026-11-15 | Class 2 (issue #7) | 13 | 13 | 0 | 0 | 351,204 | 27,016 | 1,990 | 176 | clean |
| 2026-11-15 | Class 3 (issue #8) | 9 | 9 | 0 | 0 | 316,276 | 35,142 | 823 | 384 | clean |
| 2026-11-15 | Callers (issue #9) | 20 | 18 | 0 | 2 | 591,258 | 32,848 | 1,737 | 340 | not clean at 9102aa0, clean at f85fa93 in the review of pull request #18 |

The rows of classes 1 and 2 do not hold the whole cost of their class. The matcher matched 9 of the 10 functions of class 1 and 11 of the 13 of class 2, and the lead session matched the rest. The matcher matched all 9 of class 3, and the lead session changed the tool and the form of one function. The matcher matched 17 of the 20 functions of the callers batch, and the lead session applied the reviewer's forms, which matched 0x000E3280. A lead session's tokens are not measured, so they are not in the rows. See "Class 1", "Class 2", "Class 3" and "Callers" below.

## Class 1 (issue #6, 2026-11-15)

The sources are `src/game/auto/UnkTargetBase.h` and `src/game/auto/00047D20.cpp`. The 10 required functions are `matched`, 2,031 bytes without padding. 0x00047D10 moved from `src/game/trivial/0004.cpp` to the class source, and 3315 functions are matched in all. The matched count outside the trial's files went from 3306 to 3305 because of that move only.

| Run | Tokens | Result |
|---|---:|---|
| Matcher | 203,335 | 9 matched (800 bytes). 0x00047540 parked as `register tie` at 16.2% after five attempts. |
| Lead | not measured | 0x00047540 matched with two source changes (F-0092). |
| Reviewer | 94,530 | Clean. All 10 functions pass. |

For the 9 functions of the matcher run alone, the 297,865 tokens are 33,096 per matched function and 372 per matched byte.

- **Blockers (R6):** none. Every required function is `matched`.
- **0x00047540:** it was not a register tie. The check `if (pause)` belongs after the `if` and `else` that set `pause`, and the test of bit 1 of `flags` goes through an inline accessor that returns `bool`. The matcher's report said that the control flow already agreed, and that was wrong (F-0092).
- **Reviewer:** the source holds nothing that VC71 generates (ADR-0013), and both bases' virtual functions are in slot order. The reviewer compiled the other form of five claims. Four hold. The fifth does not: 0x00047A10 also matches with named `EVec2` locals in place of `&EVec2(...)`. The source keeps `&EVec2(...)`, which is the donor's form (F-0091).
- **Review of pull request #15:** three changes, and all 10 functions stay `matched`. The header gives slots 4, 5, 7 to 11 and 13 to 15 of `UnkTargetBase` the parameter count that the `ret` of each function shows, where it declared them with no parameters. The class declares the member function 0x00047B30. The 11 stand-in classes have placeholder names (F-0091). The review also checked by test compile that VC71 puts a pointer to a member function at a multiple of 8 in a struct (F-0087).
- **Guesses in the sources:** the member names of `UnkTargetBase` other than `flags` and `player`, the names `SetMode`, `IsBuildMode` and `Flag1`, the parameter types of the base slots other than slot 2, the role words of the stand-in classes such as `Dialogs_00047D20`, and the return types of the two `PlayerInfo_00047D20` slots. The match shows only that sizes, offsets and addresses agree (F-0069).

## Class 2 (issue #7, 2026-11-15)

The source is `src/game/auto/0003B940.cpp`, with the shared header. The 13 required functions are `matched`, 1,990 bytes without padding. 0x0003B8D0 is `matched` as an extra, 112 bytes. 0x0003B2C0 and 0x0003B300 moved from `src/game/trivial/0003.cpp` to the class source, and 3327 functions are matched in all. The matched count outside the trial's files went from 3305 to 3303 because of these two moves only. Class 1's 10 rows stay `matched`.

| Run | Tokens | Result |
|---|---:|---|
| Matcher | 237,563 | 11 matched (1,634 bytes), among them the constructor with its exception-handling frame. 0x00036670 parked as `scheduling` at 94.8% after six source forms, and its thunk 0x0003B2E0 waited on it. |
| Lead | not measured | 0x00036670 matched with an inline helper in the header (F-0094), and the thunk followed. 0x0003B8D0 defined in the source in place of a `throw()` declaration (F-0095). |
| Reviewer | 113,641 | Clean. All 13 functions and the extra pass. |

For the 11 functions of the matcher run alone, the 351,204 tokens are 31,928 per matched function and 215 per matched byte.

- **Blockers (R6):** none. Every required function is `matched`.
- **0x00036670:** the difference was the order of one store and one vtable load in case 0. Case 0 holds the first two steps of 0x00124680, a call of slot 9 and the set of a flag. With these in an inline member `SetFlags` of `UnkTargetBase`, VC71 gives the original order. That the original source had such a helper is a guess (F-0094).
- **Constructor:** it has one unwind state, because 0x0003B8D0 is defined in the same source. The matcher reached that state with `throw()` on a declaration. The source now holds the definition, and the reviewer showed that its place in the file does not matter (F-0095).
- **Header:** three additions and no change of a layout or of a base slot. `EVec3` got the donor's two constructors, `UnkTargetBase` declares 0x00124680, and it has the inline `SetFlags`.
- **Reviewer:** the source holds nothing that VC71 generates (ADR-0013), and the overrides are in slot order with the parameter counts of the binary. The two list types are the plausible source, because the destructor unwinds them through two different thunks (F-0093). The reviewer compiled the other form of nine claims. Eight hold. The ninth does not: the lead's claim that 0x0003B8D0 must be defined before the constructor. The reviewer also said that the `EVec3` fill constructor has no donor evidence. That is wrong: the donor declares it in `include/engine/EVec3.h`, and the header now has the donor's form.
- **Review of pull request #16:** five source forms changed to the GameCube donor's forms, and all 14 functions stay `matched`. 0x0003C620 is a `switch (mode)`, where it was an `if` chain on a local copy of `mode`. 0x00036570 sends `player == 0 ? 0x15 : 0x16`, where it had `(player != 0) + 0x15`. The tile at +0x1C0 is one struct with one assignment, the 17 words from +0x118 are 17 members, and 0x00038D00 has one `if` less. Neither the matcher nor the reviewer had compiled the donor's forms. Four other donor forms do not match on the Xbox, and `SetFlags` matches in the derived class too (F-0093, F-0094).
- **Guesses in the sources:** the member names, `pad198` and the `EVec3` at +0x1A4, the role words and dummy slots of the stand-in classes, the dummy first virtual base of two of them, the return types of the five handler functions, `SetFlags` as a helper of the base, and 0x0003B8D0 as a static member (a free function matches too). The match shows only that sizes, offsets and addresses agree (F-0069).

## Class 3 (issue #8, 2026-11-15)

The source is `src/game/auto/000A80B0.cpp`, with the shared header unchanged. The 9 required functions are `matched`, 823 bytes without padding. No function moved from `src/game/trivial/`, so the matched count outside the trial's files stays at 3303, and 3336 functions are matched in all. The rows of classes 1 and 2 stay `matched`.

| Run | Tokens | Result |
|---|---:|---|
| Matcher | 212,242 | 9 matched. The five large overrides got empty bodies marked `parked`, because an override that is declared only resolved to the base's address. |
| Reviewer | 104,034 | Clean for the 9 functions. The five empty bodies fail, because nobody tried to match them. |
| Lead | not measured | `SetMode` as a `switch`, a `declared` line for an override in `bodecomp.match` (F-0098), and five `declared` lines in place of the bodies. |

- **Blockers (R6):** none. Every required function is `matched`.
- **The five large overrides:** an override keeps the name of the base's slot, and `bodecomp.match` resolved that `FUN_` name to the base function's address, so the vtable that the constructor and the destructor store did not compare equal. The maintainer approved a change to R1 of the plan: a `declared` line also takes an override (F-0098). The five bodies are now five `declared` lines, and the parked count is 3 again.
- **`SetMode` 0x000A8180:** the matcher's condition `newMode == 8 || (newMode > 9 && newMode <= 11)` read like the disassembly. The reviewer showed that `switch (newMode)` with the cases 8, 10 and 11 gives the same bytes, and the source now has it (F-0099).
- **Members:** the buy menu and the build menu derive from the class of 0x00145A00, which derives from `UnkTargetBase`. Their sizes 0x121C and 0x1224 are the gaps in the pause screen, and the menus' own functions prove only slightly smaller sizes (F-0100).
- **0x0008FB70:** a `generated` line for it gives `error`, so the object does not emit it.
- **Reviewer:** the source holds nothing that VC71 generates (ADR-0013), and the overrides are in slot order with the parameter counts of the binary. The reviewer compiled the other form of each claim of the matcher about a source form, and each claim holds. The matcher had not tried a `switch` in `SetMode`. The reviewer read commit aeaecae. The later commits put in the `switch` that the reviewer compiled, change the tool with its tests, and replace the bodies with `declared` lines. The 9 rows stay `matched` after each of them.
- **Guesses in the sources:** the class name and the member names, the types behind +0x24AC, +0x24B4 and +0x24C4, the stand-in classes, the size of `S_00145A00` and the last 3 bytes of each menu, the parameter types of the menu methods, and the nested `if` of the last branch of `SetMode`. The match shows only that sizes, offsets and addresses agree (F-0069).

## Callers (issue #9, 2026-11-15)

The sources are 19 new files in `src/game/auto/`, with the shared header. 18 of the 20 functions are `matched`, 1,737 bytes without padding, and 2 are parked. Beside the batch, 0x00137AF0, the deleting destructors 0x00053EE0 and 0x000BDAF0, and the thunks 0x00053D00 and 0x000BD8D0 that jump to them are `matched`. The extras 0x000AF780, 0x00026190 and 0x00026290 are `matched` too, and so is operator new 0x000136D0, which the lead matched for 0x00053DD0. 3363 functions are matched in all, 27 more than before. No function moved from `src/game/trivial/`, and the 32 required functions of classes 1 to 3 stay `matched`.

| Run | Tokens | Result |
|---|---:|---|
| Matcher | 395,928 | 17 matched (1,634 bytes). 0x000BD710 parked as `scheduling` at 79.9%, 0x000E3280 as `scheduling` at 67.0%, and 0x00017D10 as `unclassified` at 97.0%. |
| Reviewer | 195,330 | Not clean. 0x000E3280 matches with the donor's `EVec2(float)`. The member destructor of 0x000929C0 and the class `operator new` of 0x00053DD0 only steer the compiler. 0x000BD710 stays parked, at 83.7% in a form of the reviewer's. |
| Lead | not measured | The reviewer's forms, applied in four commits: 0x000E3280 `matched`, a member struct in 0x000929C0, operator new 0x000136D0 matched and named `??2@YAPAXI@Z`, the global `new` in 0x00053DD0, and the 83.7% form of 0x000BD710. |

For the 17 functions of the matcher run alone, the 591,258 tokens are 34,780 per matched function and 362 per matched byte.

- **Blockers:** 0x000BD710 is parked as `scheduling` at 83.7%. Its stores come in the original's order, and the original clears xmm0 before it loads the constant into xmm1 (F-0107). 0x00017D10 is parked as `unclassified` at 97.0%. Its unit holds 3 bytes of code at 0x00017D70 that no function starts, and its own 96 bytes are equal (F-0108).
- **0x00137AF0:** `matched` from `src/game/auto/00137AF0.cpp`. It writes the address 0x0035DC1C into the member at +0x18 of `UnkTargetBase` and returns nothing, so it is neither a vtable store nor a constructor (F-0102). Its match needs the header only for the name of its class, so it shows no gain from the shared bases.
- **0x000E3280:** the matcher parked it after about 30 forms of four `float` members. The donor's `EVec2(float value) { x = y = value; }` stores y first, and two `EVec2` members give the original's order. The donor's form was not compiled before the park, the same miss as in F-0093.
- **Header:** four additions and no change of a layout or of a base slot. `EVec2` has the donor's `EVec2(float)`. `UnkTargetBase` declares 0x00124810. The member at +0x18 is `UnkTargetText`, 4 bytes as before. `S_00145A00` moved from `src/game/auto/000A80B0.cpp`, with the 31 slots of its vtable 0x002ED510 (F-0100).
- **Forms the review settled:** a member struct that holds the class of 0x00127860 in 0x000929C0 (F-0105), the global `new` (F-0103), a class `operator delete` that calls 0x00123040 (pass, F-0106), and `throw()` on the destructor of the array member in 0x000E3200 and 0x0007CFB0 (pass with a better form named, F-0104). 0x000E3280 and 0x000F0DE0 repeat the inline base `Dialog_000E31C0`, and the reviewer showed that one shared declaration gives the same bytes. The sources keep the copies.
- **Reviewer:** the 18 matches are credible, and the sources hold nothing that VC71 generates (ADR-0013). The reviewer read commit 9102aa0. The lead's four commits after it put in the reviewer's forms, with one change: the member struct of 0x000929C0 has an implicit destructor, where the reviewer compiled `~Tracked_000929C0() {}`. Both give the same bytes. No agent read the four commits. The review of pull request #18 read all seven commits and compiled the other form of each of the lead's changes: a direct member of the class of 0x00127860 in 0x000929C0 gives 95.2%, two-argument `EVec2` members in 0x000E3280 give 88.3%, and 0x00053DD0 without the name `??2@YAPAXI@Z` gives 98.5%. It found no problem in the sources.
- **Tokens:** the headless runner stopped the matcher once, and the lead resumed it in the same context. The matcher's figure is its total at the end of the resumed run, the measure that the earlier rows use. The reviewer's figure includes one short reply to the lead.
- **Guesses in the sources:** every class name and member name, the sizes of the `pad` arrays, the types of the stand-in classes such as `Pool_00053DD0`, `Tag_00139550` and `PanelChild_000BD710`, the 8 parameter types of the constructor that 0x000BD710 calls, `unsigned short*` for the text member, and the `throw()` on the destructor of the array member. The match shows only that sizes, offsets and addresses agree (F-0069).

## Tool work (R1)

| Work | Issues | Tokens |
|---|---|---:|
| `bodecomp.match`: declared lines, the probe, generated claims | #3, #4, #5 | not measured |
| `bodecomp.match`: a declared line for an override (F-0098) | #8 | not measured |

The plan left open how the tokens of a lead session are measured, and that is not settled. The build sessions of issues #3 and #4 reported no total. A session's transcript records the usage of each response, so a total can be read from it after the rule is chosen.

## Probe of a class 1 skeleton (issue #4, 2026-11-15)

Two risks would stop the whole trial, so a scratch skeleton of class 1 checked them before any class work. The skeleton is `class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0` with the constructor, the destructor and the four overrides. It is not under `src/`, and its bodies are not match attempts. It went through `bodecomp.match.check_source`.

### Thunks

VC71 emits the three thunks with the original bytes, at `/O2 /G7 /arch:SSE` and with `/GX` added (F-0087).

| Address | Original | Built | Built jump names |
|---|---|---|---|
| 0x00047CE0 | `2b49fc81e9ec000000e9e2010000`, jump to 0x00047ED0 | `2b49fc81e9ec000000e9` and a REL32 relocation | `??_EUnk8003AA6C@@UAEPAXI@Z`, which stands for the deleting destructor |
| 0x00047CF0 | `2b49fce928f8ffff`, jump to 0x00047520 | `2b49fce9` and a REL32 relocation | the override of slot 1 |
| 0x00047D00 | `2b49fce908000000`, jump to 0x00047D10 | `2b49fce9` and a REL32 relocation | the override of slot 2 |

`check_source` reports the destructor 0x000474C0 and the overrides 0x00047520 and 0x00047D10 as `matched`. The destructor stores both vtables, so its match needs the 17 slots of the main vtable, the three thunks and the deleting destructor 0x00047ED0 to compare equal with the original. The built vbtable is `bcffffffa8000000`, the bytes at 0x002E3AC8.

### Exception-handling chain

At `/O2 /G7 /arch:SSE`, the default flags when the probe ran, VC71 emits no exception-handling frame, so the constructor cannot match. With `/GX` added it emits the frame, and the chain compares equal (F-0088).

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

With `/GX` added, every claimed source gives the same row as before: 3306 matched, 3 parked, and `config/functions.csv` is equal. The maintainer chose on 2026-11-15 to make `/GX` a default flag (ADR-0017).
