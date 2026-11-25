# Function ledger

Generated from `config/symbols.txt` and `config/functions.csv` by `uv run python -m bodecomp.ledger`; do not edit.
Check that it is current with `uv run python -m bodecomp.ledger --check`.
Bytes are function sizes from Ghidra; code outside every function (F-0026) is not counted.

| Status | Meaning | Functions | Share | Bytes | Share |
|---|---|---:|---:|---:|---:|
| `sdk` | SDK function named from a unique XDK library match | 2,159 | 9.9% | 328,477 | 14.0% |
| `sdk-ambiguous` | SDK function whose bytes match several library functions | 459 | 2.1% | 22,658 | 1.0% |
| `sdk-section` | SDK function named only by its XBE section | 71 | 0.3% | 28,411 | 1.2% |
| `sdk-other` | SDK function named by the XBE loader or Ghidra Function ID | 150 | 0.7% | 29,158 | 1.2% |
| `matched` | game function whose C++ compiles to its original bytes | 2 | 0.0% | 21 | 0.0% |
| `gc` | game function named from the GameCube symbols, with two kinds of evidence | 0 | 0.0% | 0 | 0.0% |
| `string` | game function named from its own strings | 497 | 2.3% | 253,044 | 10.7% |
| `open` | game function with Ghidra's automatic name | 18,399 | 84.6% | 1,692,684 | 71.9% |
| **all** | | **21,737** | | **2,354,453** | |

Data labels in `symbols.txt`: 210 (not counted above).

## Game functions by name tier

| Tier | Functions | Share | Bytes | Share |
|---|---:|---:|---:|---:|
| `matched` | 2 | 0.0% | 21 | 0.0% |
| `gc` | 0 | 0.0% | 0 | 0.0% |
| `string` | 497 | 2.6% | 253,044 | 13.0% |
| `auto` | 18,399 | 97.4% | 1,692,684 | 87.0% |
| **all game** | **18,898** | | **1,945,749** | |

Named game functions: 499 of 18,898 (2.6%).

## Game functions by match status

A matched function keeps its `auto` name when its source uses placeholder names (ADR-0011).

| Status | Functions | Share | Bytes | Share |
|---|---:|---:|---:|---:|
| `matched` | 3,945 | 20.9% | 35,219 | 1.8% |
| `nonmatching` | 0 | 0.0% | 0 | 0.0% |
| `parked` | 46 | 0.2% | 1,401 | 0.1% |
| `error` | 0 | 0.0% | 0 | 0.0% |
| `open` | 14,907 | 78.9% | 1,909,129 | 98.1% |
