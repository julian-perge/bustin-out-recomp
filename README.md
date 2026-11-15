# The Sims Bustin' Out (Xbox) decomp

A byte-matching decompilation of the Xbox release of The Sims Bustin' Out: C++ source that
Microsoft's VC71 compiler builds back into the original bytes of `default.xbe`.

The GameCube decomp ([daftblazer/bustin-out-decomp](https://github.com/daftblazer/bustin-out-decomp))
provides names, types and draft C++. The method is in
[docs/METHODOLOGY.md](docs/METHODOLOGY.md), and the
current state is in [docs/STATUS.md](docs/STATUS.md).

## Progress

<!-- progress:start -->

<p align="center">
  <img src="https://img.shields.io/badge/Game_code_matched-0.45%25-3828f7" alt="Game code matched: 0.45%">
  <img src="https://img.shields.io/badge/Functions_matched-2,324_%2F_18,894-3828f7" alt="Functions matched: 2,324 / 18,894">
  <img src="https://img.shields.io/badge/Game_functions_named-497_%2F_18,894-3828f7" alt="Game functions named: 497 / 18,894">
</p>

| Progress | Functions | Code | |
|---|---:|---:|---|
| Game code matched from C++ | 2,324 / 18,894 | 0.45% | `[#-------------------]` |
| Game code named | 497 / 18,894 | 13.01% | `[###-----------------]` |
| Xbox SDK named from a unique XDK library match | 2,158 / 2,838 | 80.37% | `[################----]` |

A game function counts as matched only when its C++ source compiles with VC71 to the original bytes.
Matching so far: 2,324 matched, 0 nonmatching, 3 parked.
The SDK functions come from Microsoft's XDK libraries and are named, not decompiled.
Code percentages are of function bytes; code outside every function is not counted. Per-function detail is in [docs/LEDGER.md](docs/LEDGER.md).

<!-- progress:end -->

Refresh this section with `uv run python -m bodecomp.readme`.

## Working on it

See [AGENTS.md](AGENTS.md) for where things live and the working rules, and
[docs/WORKFLOW.md](docs/WORKFLOW.md) for the tool procedures. This repo does not ship the game;
you need your own copy of `default.xbe`.
