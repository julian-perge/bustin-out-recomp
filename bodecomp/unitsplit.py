from __future__ import annotations

import argparse
import bisect
import sys
from dataclasses import dataclass
from pathlib import Path

from bodecomp.coff import CoffSection, Reloc, Symbol, parse
from bodecomp.coffwrite import write_coff
from bodecomp.split import UNITS, read_units
from bodecomp.xbe import Xbe

TARGET = Path("build/target")
RELOCS = TARGET / "relocs.tsv"
SYMBOL_TABLE = TARGET / "symbols.tsv"
CODE = 0x60000020
DIR32, REL32 = 0x6, 0x14
FUNCTION, EXTERNAL, STATIC, FILE = 0x20, 2, 3, 103


@dataclass(frozen=True)
class DelinkReloc:
    address: int
    kind: str
    width: int
    target: int
    addend: int
    # None for a relocation the exporter always keeps; otherwise the primary
    # reference targets of its instruction, and the exporter drops it from a unit
    # that contains all of them.
    refs: tuple[int, ...] | None


@dataclass(frozen=True)
class NamedAddress:
    name: str
    function: bool
    static: bool


def read_relocs(path: Path) -> list[DelinkReloc]:
    out = []
    for line in path.read_text().splitlines():
        address, kind, width, bitmask, target, addend, refs = line.split("\t")
        if (width, bitmask) not in (("4", "FFFFFFFF"), ("1", "FF")) or kind not in (
            "A",
            "R",
        ):
            raise ValueError(f"unsupported relocation: {line}")
        out.append(
            DelinkReloc(
                int(address, 16),
                kind,
                int(width),
                int(target, 16),
                int(addend),
                None
                if refs == "-"
                else tuple(int(r, 16) for r in refs[2:].split(",") if r),
            )
        )
    return sorted(out, key=lambda r: r.address)


def read_symbol_table(path: Path) -> dict[int, NamedAddress]:
    out = {}
    for line in path.read_text().splitlines():
        address, function, static, name = line.split("\t", 3)
        out[int(address, 16)] = NamedAddress(name, function == "1", static == "1")
    return out


def _kept(r: DelinkReloc, start: int, end: int) -> bool:
    return r.refs is None or any(not start <= t < end for t in r.refs)


def build_unit(
    start: int,
    end: int,
    text: bytes,
    text_va: int,
    relocs: list[DelinkReloc],
    names: dict[int, NamedAddress],
    comment: CoffSection,
) -> tuple[list[CoffSection], list[Symbol]]:
    """Builds one unit as the delinker's COFF exporter would, from the tables
    tools/ghidra_scripts/ExportDelinkTables.java writes."""

    def name(address: int) -> NamedAddress:
        if address not in names:
            raise KeyError(f"no symbol at 0x{address:08X}")
        return names[address]

    data = bytearray(text[start - text_va : end - text_va])
    inside = [r for r in relocs if start <= r.address < end]
    kept = []
    for r in inside:
        # The exporter logs a relocation narrower than four bytes as unknown and
        # leaves its bytes as they are.
        if r.width != 4 or not _kept(r, start, end):
            continue
        value = r.addend + (r.width if r.kind == "R" else 0)
        offset = r.address - start
        data[offset : offset + 4] = (value & 0xFFFFFFFF).to_bytes(4, "little")
        kind = REL32 if r.kind == "R" else DIR32
        kept.append(Reloc(offset, name(r.target).name, kind))

    defined = [
        Symbol(
            n.name,
            address - start,
            1,
            FUNCTION if n.function else 0,
            STATIC if n.static else EXTERNAL,
        )
        for address, n in names.items()
        if start <= address < end
    ]
    # The exporter names every target outside the unit that has a symbol as an
    # undefined external, including the targets of relocations it drops.
    outside = {
        r.target for r in inside if not start <= r.target < end and r.target in names
    }
    undefined = [Symbol(name(t).name, 0, 0, FUNCTION, EXTERNAL) for t in outside]
    symbols = [Symbol(".file", 0, -2, 0, FILE), Symbol(".text", 0, 1, 0, STATIC)]
    symbols += sorted(defined, key=lambda s: (s.value, s.name))
    symbols += sorted(undefined, key=lambda s: s.name)
    text_section = CoffSection(".text", bytes(data), tuple(kept), CODE)
    return [text_section, comment], symbols


def split(
    xbe_path: Path,
    text_obj: Path,
    units_path: Path,
    relocs_path: Path,
    symbols_path: Path,
    out: Path,
) -> int:
    xbe = Xbe.parse(xbe_path.read_bytes())
    section = next(s for s in xbe.sections if s.name == ".text")
    text = xbe.read(section.va, section.raw_size)
    relocs = read_relocs(relocs_path)
    reloc_at = [r.address for r in relocs]
    names = read_symbol_table(symbols_path)
    named_at = sorted(names)
    comment = parse(text_obj.read_bytes()).sections[1]
    out.mkdir(parents=True, exist_ok=True)
    units = read_units(units_path)
    for u in units:
        lo = bisect.bisect_left(reloc_at, u.start)
        hi = bisect.bisect_left(reloc_at, u.end)
        unit_relocs = relocs[lo:hi]
        a = bisect.bisect_left(named_at, u.start)
        b = bisect.bisect_left(named_at, u.end)
        local = {k: names[k] for k in named_at[a:b]}
        local.update(
            {r.target: names[r.target] for r in unit_relocs if r.target in names}
        )
        sections, symbols = build_unit(
            u.start, u.end, text, section.va, unit_relocs, local, comment
        )
        (out / f"{u.start:08X}.obj").write_bytes(write_coff(sections, symbols))
    return len(units)


def compare(ours: Path, reference: Path) -> list[str]:
    problems = []
    for ref in sorted(reference.glob("*.obj")):
        mine = ours / ref.name
        if not mine.exists():
            problems.append(f"{ref.name}: missing")
            continue
        a, b = parse(mine.read_bytes()), parse(ref.read_bytes())
        if a.sections != b.sections:
            problems.append(f"{ref.name}: sections differ")
        elif a.symbols != b.symbols:
            problems.append(f"{ref.name}: symbols differ")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.unitsplit")
    parser.add_argument("--xbe", type=Path, default=Path("orig/default.xbe"))
    parser.add_argument("--text-obj", type=Path, default=TARGET / "text.obj")
    parser.add_argument("--units", type=Path, default=UNITS)
    parser.add_argument("--relocs", type=Path, default=RELOCS)
    parser.add_argument("--symbols", type=Path, default=SYMBOL_TABLE)
    parser.add_argument("--out", type=Path, default=TARGET / "units")
    parser.add_argument(
        "--compare", type=Path, help="compare --out with objects Ghidra exported"
    )
    args = parser.parse_args(argv)
    if args.compare:
        problems = compare(args.out, args.compare)
        for line in problems[:40]:
            print(line)
        print(f"{len(problems)} objects differ")
        return 1 if problems else 0
    count = split(
        args.xbe, args.text_obj, args.units, args.relocs, args.symbols, args.out
    )
    print(f"units written {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
