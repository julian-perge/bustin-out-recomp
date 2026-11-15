from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bodecomp.symbols import read_symbols
from bodecomp.xbe import Xbe

UNITS = Path("build/target/units.txt")


@dataclass(frozen=True)
class Unit:
    start: int
    end: int


def partition(text_start: int, text_end: int, starts: list[int]) -> list[Unit]:
    points = sorted({s for s in starts if text_start <= s < text_end} | {text_start})
    ends = points[1:] + [text_end]
    return [Unit(a, b) for a, b in zip(points, ends, strict=True)]


def write_units(path: Path, units: list[Unit]) -> None:
    path.write_text("".join(f"{u.start:08X} {u.end:08X}\n" for u in units))


def read_units(path: Path) -> list[Unit]:
    units = []
    for line in path.read_text().splitlines():
        start, end = line.split()
        units.append(Unit(int(start, 16), int(end, 16)))
    return units


def main() -> None:
    xbe = Xbe.parse(Path("orig/default.xbe").read_bytes())
    text = next(s for s in xbe.sections if s.name == ".text")
    starts = [
        e.address
        for e in read_symbols(Path("config/symbols.txt"))
        if e.kind == "function"
    ]
    units = partition(text.va, text.va + text.raw_size, starts)
    UNITS.parent.mkdir(parents=True, exist_ok=True)
    write_units(UNITS, units)
    print(f"wrote {len(units)} units to {UNITS}")


if __name__ == "__main__":
    main()
