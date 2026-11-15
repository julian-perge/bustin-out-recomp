from __future__ import annotations

import re
import struct
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from bodecomp.coff import Coff, parse
from bodecomp.split import Unit, read_units
from bodecomp.symbols import read_symbols
from bodecomp.xbe import Xbe

ADDRESS_SUFFIX = re.compile(r"_([0-9A-Fa-f]{8})$")
DIR32, REL32 = 0x6, 0x14


@dataclass
class Report:
    mismatches: list[int] = field(default_factory=list)
    unresolved: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.mismatches and not self.unresolved


def resolve(name: str, table: dict[str, int]) -> int | None:
    if name in table:
        return table[name]
    # The delinker qualifies names with their Ghidra namespace, for example
    # D3D8::D3DDevice_Clear, while symbols.txt holds the plain name.
    plain = name.rsplit("::", 1)[-1]
    if plain in table:
        return table[plain]
    # A call to an imported function lands on its import stub in .text, which
    # the sync names thunk_<name>; the delinker names the import instead.
    if "::" in name and "thunk_" + plain in table:
        return table["thunk_" + plain]
    match = ADDRESS_SUFFIX.search(name)
    return int(match.group(1), 16) if match else None


def _text_index(coff: Coff) -> int:
    return next(i for i, s in enumerate(coff.sections) if s.name == ".text")


def local_symbols(start: int, coff: Coff) -> dict[str, int]:
    number = _text_index(coff) + 1
    return {s.name: start + s.value for s in coff.symbols if s.section == number}


def relink(
    units: list[tuple[int, Coff]], table: dict[str, int], original: bytes, text_va: int
) -> Report:
    image = bytearray(len(original))
    writes = bytearray(len(original))
    unresolved: Counter[str] = Counter()
    for start, coff in units:
        section = coff.sections[_text_index(coff)]
        local = local_symbols(start, coff)
        data = bytearray(section.data)
        for r in section.relocs:
            target = local[r.symbol] if r.symbol in local else resolve(r.symbol, table)
            if target is None:
                unresolved[r.symbol] += 1
                continue
            (addend,) = struct.unpack_from("<i", data, r.offset)
            if r.type == DIR32:
                value = target + addend
            elif r.type == REL32:
                value = target + addend - (start + r.offset + 4)
            else:
                raise ValueError(f"unsupported relocation type {r.type:#x}")
            struct.pack_into("<I", data, r.offset, value & 0xFFFFFFFF)
        offset = start - text_va
        image[offset : offset + len(data)] = data
        for i in range(offset, offset + len(data)):
            writes[i] += 1
    # A byte no unit wrote, or that two units wrote, counts as a mismatch even
    # when its value happens to agree with the original.
    mismatches = [
        text_va + i
        for i, (a, b) in enumerate(zip(image, original, strict=True))
        if a != b or writes[i] != 1
    ]
    return Report(mismatches, dict(unresolved))


def unit_problems(expected: list[Unit], units: list[tuple[int, Coff]]) -> list[str]:
    spans = {u.start: u.end - u.start for u in expected}
    sizes = {start: len(c.sections[_text_index(c)].data) for start, c in units}
    problems = []
    for start in sorted(spans.keys() | sizes.keys()):
        if start not in sizes:
            problems.append(f"0x{start:08X}: no object")
        elif start not in spans:
            problems.append(f"0x{start:08X}: object not in the units list")
        elif sizes[start] != spans[start]:
            problems.append(
                f"0x{start:08X}: object has {sizes[start]} bytes, "
                f"units list says {spans[start]}"
            )
    return problems


def main() -> None:
    xbe = Xbe.parse(Path("orig/default.xbe").read_bytes())
    text = next(s for s in xbe.sections if s.name == ".text")
    units = [
        (int(p.stem, 16), parse(p.read_bytes()))
        for p in sorted(Path("build/target/units").glob("*.obj"))
    ]
    problems = unit_problems(read_units(Path("build/target/units.txt")), units)
    table: dict[str, int] = {}
    for start, coff in units:
        for name, address in local_symbols(start, coff).items():
            if not name.startswith("."):
                table.setdefault(name, address)
    for e in read_symbols(Path("config/symbols.txt")):
        table.setdefault(e.name, e.address)
    report = relink(units, table, xbe.read(text.va, text.raw_size), text.va)
    lines = [f"units {len(units)}", f"mismatched bytes {len(report.mismatches)}"]
    lines += [f"  0x{a:08X}" for a in report.mismatches[:200]]
    lines.append(f"unresolved names {len(report.unresolved)}")
    lines += [f"  {n} x{c}" for n, c in sorted(report.unresolved.items())[:200]]
    lines.append(f"unit problems {len(problems)}")
    lines += [f"  {p}" for p in problems[:200]]
    Path("build/relink-report.txt").write_text("\n".join(lines) + "\n")
    print(lines[0])
    print(lines[1])
    print(f"unresolved names {len(report.unresolved)}")
    print(f"unit problems {len(problems)}")
    sys.exit(0 if report.ok and not problems else 1)


if __name__ == "__main__":
    main()
