from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bodecomp.ledger import GAME, SYMBOLS, status
from bodecomp.match import FUNCTIONS, read_functions
from bodecomp.symbols import Entry, read_symbols

README = Path("README.md")
START, END = "<!-- progress:start -->", "<!-- progress:end -->"
COLOR = "3828f7"
SDK = ("sdk", "sdk-ambiguous", "sdk-section", "sdk-other")


def bar(part: int, whole: int, width: int = 20) -> str:
    filled = round(width * part / whole) if whole else 0
    if part and not filled:
        filled = 1
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def badge(label: str, value: str) -> str:
    def escape(text: str) -> str:
        for old, new in (
            ("-", "--"),
            ("_", "__"),
            (" ", "_"),
            ("%", "%25"),
            ("/", "%2F"),
        ):
            text = text.replace(old, new)
        return text

    url = f"https://img.shields.io/badge/{escape(label)}-{escape(value)}-{COLOR}"
    return f'<img src="{url}" alt="{label}: {value}">'


def _percent(part: int, whole: int) -> str:
    return f"{100 * part / whole:.2f}%" if whole else "0.00%"


def render(entries: list[Entry], matches: dict[int, tuple[str, str]]) -> str:
    functions = [e for e in entries if e.kind == "function"]
    game = [e for e in functions if status(e) in dict(GAME).values()]
    sdk = [e for e in functions if status(e) in SDK]
    game_bytes = sum(e.size for e in game)
    matched = [e for e in game if matches.get(e.address, ("open", ""))[0] == "matched"]
    matched_bytes = sum(e.size for e in matched)
    named = [e for e in game if e.tier != "auto"]
    named_bytes = sum(e.size for e in named)
    library = [e for e in sdk if status(e) == "sdk"]
    library_bytes = sum(e.size for e in library)
    sdk_bytes = sum(e.size for e in sdk)
    by_status = {
        name: sum(1 for e in game if matches.get(e.address, ("open", ""))[0] == name)
        for name in ("matched", "nonmatching", "parked")
    }
    rows = (
        ("Game code matched from C++", matched, game, matched_bytes, game_bytes),
        ("Game code named", named, game, named_bytes, game_bytes),
        (
            "Xbox SDK named from a unique XDK library match",
            library,
            sdk,
            library_bytes,
            sdk_bytes,
        ),
    )
    out = [
        START,
        "",
        '<p align="center">',
        "  " + badge("Game code matched", _percent(matched_bytes, game_bytes)),
        "  " + badge("Functions matched", f"{len(matched):,} / {len(game):,}"),
        "  " + badge("Game functions named", f"{len(named):,} / {len(game):,}"),
        "</p>",
        "",
        "| Progress | Functions | Code | |",
        "|---|---:|---:|---|",
    ]
    for label, part, whole, part_bytes, whole_bytes in rows:
        out.append(
            f"| {label} | {len(part):,} / {len(whole):,}"
            f" | {_percent(part_bytes, whole_bytes)}"
            f" | `{bar(part_bytes, whole_bytes)}` |"
        )
    out += [
        "",
        "A game function counts as matched only when its C++ source compiles with VC71"
        " to the original bytes.",
        f"Matching so far: {by_status['matched']:,} matched,"
        f" {by_status['nonmatching']:,} nonmatching,"
        f" {by_status['parked']:,} parked.",
        "The SDK functions come from Microsoft's XDK libraries and are named, not"
        " decompiled.",
        "Code percentages are of function bytes; code outside every function is not"
        " counted. Per-function detail is in [docs/LEDGER.md](docs/LEDGER.md).",
        "",
        END,
    ]
    return "\n".join(out)


def replace(text: str, block: str) -> str:
    if START not in text or END not in text:
        raise ValueError(f"README has no {START} ... {END} block")
    i, j = text.index(START), text.index(END) + len(END)
    return text[:i] + block + text[j:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.readme")
    parser.add_argument("--symbols", type=Path, default=SYMBOLS)
    parser.add_argument("--functions", type=Path, default=FUNCTIONS)
    parser.add_argument("--readme", type=Path, default=README)
    args = parser.parse_args(argv)
    block = render(read_symbols(args.symbols), read_functions(args.functions))
    args.readme.write_text(replace(args.readme.read_text(), block))
    print(f"wrote the progress block of {args.readme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
