from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

HEADER = ("address", "kind", "size", "name", "tier", "evidence")
# A Ghidra auto name followed by address suffixes that earlier syncs added.
SUFFIXED_AUTO = re.compile(
    r"^((?:thunk_)?(?:FUN|DAT|LAB|PTR)_[0-9a-fA-F]{8})(?:_[0-9A-F]{8})+$"
)


@dataclass(frozen=True)
class Entry:
    address: int
    kind: str
    size: int
    name: str
    tier: str
    evidence: str


def _order(entry: Entry) -> tuple[int, str]:
    return entry.address, entry.kind


def read_symbols(path: Path) -> list[Entry]:
    with path.open(newline="") as f:
        rows = csv.reader(f, delimiter="\t")
        header = tuple(next(rows))
        if header != HEADER:
            raise ValueError(
                f"{path} header is {list(header)}, expected {list(HEADER)}"
            )
        return [Entry(int(r[0], 16), r[1], int(r[2]), r[3], r[4], r[5]) for r in rows]


def write_symbols(path: Path, entries: list[Entry]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        for e in sorted(entries, key=_order):
            writer.writerow(
                [f"0x{e.address:08X}", e.kind, e.size, e.name, e.tier, e.evidence]
            )


def _base(entry: Entry) -> str:
    if entry.tier != "auto":
        return entry.name
    match = SUFFIXED_AUTO.match(entry.name)
    return match.group(1) if match else entry.name


def make_unique(entries: list[Entry]) -> list[Entry]:
    ordered = [replace(e, name=_base(e)) for e in sorted(entries, key=_order)]
    counts = Counter(e.name for e in ordered)
    taken = {e.name for e in ordered if counts[e.name] == 1}
    out = []
    for e in ordered:
        name = e.name
        if counts[e.name] > 1:
            if e.tier == "auto" or name in taken:
                name = f"{e.name}_{e.address:08X}"
                serial = 1
                while name in taken:
                    name = f"{e.name}_{e.address:08X}_{serial}"
                    serial += 1
            taken.add(name)
        out.append(replace(e, name=name))
    return out
