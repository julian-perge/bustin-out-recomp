from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from bodecomp.match import FUNCTIONS, read_functions
from bodecomp.symbols import Entry, read_symbols

SYMBOLS = Path("config/symbols.txt")
LEDGER = Path("docs/LEDGER.md")
STATUSES = (
    ("sdk", "SDK function named from a unique XDK library match"),
    ("sdk-ambiguous", "SDK function whose bytes match several library functions"),
    ("sdk-section", "SDK function named only by its XBE section"),
    ("sdk-other", "SDK function named by the XBE loader or Ghidra Function ID"),
    ("matched", "game function whose C++ compiles to its original bytes"),
    ("gc", "game function named from the GameCube symbols, with two kinds of evidence"),
    ("string", "game function named from its own strings"),
    ("open", "game function with Ghidra's automatic name"),
)
GAME = (("matched", "matched"), ("gc", "gc"), ("string", "string"), ("auto", "open"))


def status(entry: Entry) -> str:
    if entry.tier == "auto":
        return "open"
    if entry.tier in ("matched", "gc", "string"):
        return entry.tier
    if entry.tier == "sdk":
        if entry.evidence.startswith("lib-ambiguous"):
            return "sdk-ambiguous"
        if entry.evidence.startswith("lib:"):
            return "sdk"
        if entry.evidence.startswith("section:"):
            return "sdk-section"
        return "sdk-other"
    raise ValueError(
        f"0x{entry.address:08X} {entry.name}: tier {entry.tier!r} has no ledger "
        "status; add one to bodecomp/ledger.py"
    )


def _share(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}%" if whole else "0.0%"


def render(
    entries: list[Entry], matches: dict[int, tuple[str, str]] | None = None
) -> str:
    matches = matches or {}
    functions = [e for e in entries if e.kind == "function"]
    counts: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    for entry in functions:
        name = status(entry)
        counts[name] += 1
        sizes[name] += entry.size
    total, total_bytes = len(functions), sum(sizes.values())
    data = sum(1 for e in entries if e.kind == "data")
    lines = [
        "# Function ledger",
        "",
        "Generated from `config/symbols.txt` and `config/functions.csv` by"
        " `uv run python -m bodecomp.ledger`;"
        " do not edit.",
        "Check that it is current with `uv run python -m bodecomp.ledger --check`.",
        "Bytes are function sizes from Ghidra; code outside every function"
        " (F-0026) is not counted.",
        "",
        "| Status | Meaning | Functions | Share | Bytes | Share |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, meaning in STATUSES:
        lines.append(
            f"| `{name}` | {meaning} | {counts[name]:,} | {_share(counts[name], total)}"
            f" | {sizes[name]:,} | {_share(sizes[name], total_bytes)} |"
        )
    lines.append(f"| **all** | | **{total:,}** | | **{total_bytes:,}** | |")
    game = sum(counts[name] for _, name in GAME)
    game_bytes = sum(sizes[name] for _, name in GAME)
    named = counts["matched"] + counts["gc"] + counts["string"]
    lines += [
        "",
        f"Data labels in `symbols.txt`: {data:,} (not counted above).",
        "",
        "## Game functions by name tier",
        "",
        "| Tier | Functions | Share | Bytes | Share |",
        "|---|---:|---:|---:|---:|",
    ]
    for tier, name in GAME:
        lines.append(
            f"| `{tier}` | {counts[name]:,} | {_share(counts[name], game)}"
            f" | {sizes[name]:,} | {_share(sizes[name], game_bytes)} |"
        )
    lines.append(f"| **all game** | **{game:,}** | | **{game_bytes:,}** | |")
    lines += [
        "",
        f"Named game functions: {named:,} of {game:,} ({_share(named, game)}).",
        "",
        "## Game functions by match status",
        "",
        "A matched function keeps its `auto` name when its source uses placeholder"
        " names (ADR-0011).",
        "",
        "| Status | Functions | Share | Bytes | Share |",
        "|---|---:|---:|---:|---:|",
    ]
    by_match: Counter[str] = Counter()
    match_bytes: Counter[str] = Counter()
    for entry in functions:
        if status(entry) in dict(GAME).values():
            name = matches.get(entry.address, ("open", ""))[0]
            by_match[name] += 1
            match_bytes[name] += entry.size
    for name in ("matched", "nonmatching", "parked", "error", "open"):
        lines.append(
            f"| `{name}` | {by_match[name]:,} | {_share(by_match[name], game)}"
            f" | {match_bytes[name]:,} | {_share(match_bytes[name], game_bytes)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.ledger")
    parser.add_argument("--symbols", type=Path, default=SYMBOLS)
    parser.add_argument("--functions", type=Path, default=FUNCTIONS)
    parser.add_argument("--out", type=Path, default=LEDGER)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    matches = read_functions(args.functions) if args.functions.exists() else {}
    text = render(read_symbols(args.symbols), matches)
    if args.check:
        if not args.out.exists() or args.out.read_text() != text:
            print(f"{args.out} is stale; run uv run python -m bodecomp.ledger")
            return 1
        return 0
    args.out.write_text(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
