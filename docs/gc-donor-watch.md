# GameCube decomp watch

A log of what daftblazer/bustin-out-decomp (GameCube `G4ME69`) has pushed, and what each change could give the Xbox decomp. Each check, run on request, appends one entry when there are new commits. The newest entry's last SHA is where the next check starts.

## 2026-10-10 baseline (last seen 5c0eece8)

- There were 35 commits on 2026-10-10, all in the Apt UI library: EA's Flash-style UI player, which runs a small ActionScript virtual machine. Their README reports 578 matched functions (3.97%).
- Files besides `src/`: `include/ui/Apt.h`, `docs/ui-notes/*.md` (notes per address range, from 0x8012AD10 to 0x80152020), `config/G4ME69/splits.txt`, `config/G4ME69/symbols.txt`, `tools/tu0.sh`.
- Matched so far: the String natives (indexOf, slice, split, substr, case conversion), the Mersenne Twister seed and draw, value classes (number, boolean, array, function, date), the operand stack, the message queue, display lists, timeline helpers, and shape and mask drawing.
- Why it matters for the Xbox decomp: the Xbox strings include `.\aptauxpceorgl.cpp`, which suggests Apt is in the Xbox build too. That is a preliminary raw-search finding until Ghidra confirms it. If it holds, `Apt.h` and these names are `gc` tier candidates. The gperf keyword table they mention is generated code, so its strings and layout should be the same on both platforms, which makes it a good cross-platform anchor.

## 2026-10-11 (last seen d8483a60)

- 43 commits since 5c0eece8, pushed 2026-10-10 between 21:55 and 23:57 UTC. Their README now reports 1,829 of 10,848 functions matched (6.24%), up from 578 (3.97%). Game code (`sims/`) is at 1,537 of 3,289 functions; the engine, the runtimes and the SDK are still at 0.
- Judging by the commit messages, most of the jump came from `tools/gen_trivial.py`. It reads a unit's small functions from `symbols.txt`, recognises a few shapes in the disassembly (empty functions, getters, setters, runs of member stores, virtual destructors that store a vtable and call delete), writes source for them, compiles, and keeps only the functions that match. It added 14 new `sims/` units this way, one of them with 154 trivial functions.
- Apt UI work continued in the 8012F420 and 8013C054 units: value constructors, type tests and releases, the named pool class (`UiNamedPool`), `UiObj::Draw`, PlaceObject and goto-frame command runners, and the event queue. `include/ui/Apt.h` gained six `AptValue` methods, and `symbols.txt` renamed 16 Apt functions.
- They found that the Apt library was built at -O0, while the rest of the game uses -O2. `configure.py` now builds that library with its own flags.
- New notes in `docs/ui-notes/`: `apt-core-functions.md` (the 2x3 affine point transform, the button event mask to clip event flag table, the event queue layout, the value-to-integer conversion), `matching-idioms.md` (GCC 2.95 -O0 trailing-branch idioms, which are specific to their compiler), and `world-to-screen.md` (how `E3DWindow::TransformToScreen` projects a world point to frame-buffer pixels, and a widescreen fix for 2D drawn at a world position).
- What could transfer to the Xbox side:
  - A shape-based generator for trivial functions is worth building for VC71. Their total rose by about 1,250 functions in two hours, mostly through it. The shapes differ on x86, but the generate, compile and keep-if-match loop is the same, and it fits our flow of matching functions before grouping them into files.
  - The Xbox Apt code may also have been built with different flags from the `/O2 /G7 /arch:SSE` default. Try other flags first if Apt functions fail to match at the default. This is preliminary: nothing about the Xbox Apt flags has been checked.
  - The Apt class and method names, the event flag table and the value type numbering are `gc` tier candidates. The Xbox Apt code sits in the orphaned 29% of `.text` that M1 found, so it needs units before any of this can be applied.
  - `world-to-screen.md` matters for the phase 2 harness rather than for matching: the same drift of 2D elements toward the centre will appear if the Xbox recomp widens the projection.
