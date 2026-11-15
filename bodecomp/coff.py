from __future__ import annotations

import struct
from dataclasses import dataclass, replace

FUNCTION_TYPE = 0x20
WEAK_EXTERNAL = 105
RELOC_WIDTHS = {0x6: 4, 0x7: 4, 0xA: 2, 0xB: 4, 0x14: 4}


@dataclass(frozen=True)
class Reloc:
    offset: int
    symbol: str
    type: int


@dataclass(frozen=True)
class CoffSection:
    name: str
    data: bytes
    relocs: tuple[Reloc, ...]
    characteristics: int


@dataclass(frozen=True)
class Symbol:
    name: str
    value: int
    section: int
    type: int
    storage_class: int
    alias: str | None = None


@dataclass(frozen=True)
class Coff:
    sections: tuple[CoffSection, ...]
    symbols: tuple[Symbol, ...]


def _read_name(raw: bytes, strings: bytes) -> str:
    if raw[:4] == b"\0\0\0\0":
        (offset,) = struct.unpack_from("<I", raw, 4)
        end = strings.index(b"\0", offset)
        return strings[offset:end].decode("ascii")
    return raw.split(b"\0")[0].decode("ascii")


def parse(data: bytes) -> Coff:
    _, section_count, _, symtab_offset, symbol_count, optional_size, _ = (
        struct.unpack_from("<HHIIIHH", data, 0)
    )
    strings_offset = symtab_offset + 18 * symbol_count
    strings = data[strings_offset:]

    by_index: dict[int, Symbol] = {}
    tags: dict[int, int] = {}
    index = 0
    while index < symbol_count:
        offset = symtab_offset + 18 * index
        raw_name = data[offset : offset + 8]
        value, section, stype, storage, aux_count = struct.unpack_from(
            "<IhHBB", data, offset + 8
        )
        name = _read_name(raw_name, strings)
        by_index[index] = Symbol(name, value, section, stype, storage)
        if storage == WEAK_EXTERNAL and aux_count:
            (tags[index],) = struct.unpack_from("<I", data, offset + 18)
        index += 1 + aux_count
    for index, tag in tags.items():
        by_index[index] = replace(by_index[index], alias=by_index[tag].name)

    sections = []
    header_offset = 20 + optional_size
    for i in range(section_count):
        offset = header_offset + 40 * i
        raw_name = data[offset : offset + 8]
        (
            _,
            _,
            raw_size,
            raw_pointer,
            reloc_pointer,
            _,
            reloc_count,
            _,
            characteristics,
        ) = struct.unpack_from("<IIIIIIHHI", data, offset + 8)
        name = raw_name.split(b"\0")[0].decode("ascii")
        relocs = []
        for r in range(reloc_count):
            r_offset, symbol_index, rtype = struct.unpack_from(
                "<IIH", data, reloc_pointer + 10 * r
            )
            relocs.append(Reloc(r_offset, by_index[symbol_index].name, rtype))
        section_data = data[raw_pointer : raw_pointer + raw_size]
        sections.append(CoffSection(name, section_data, tuple(relocs), characteristics))

    return Coff(tuple(sections), tuple(by_index.values()))


def find_symbol(coff: Coff, name: str) -> Symbol:
    matches = [
        s
        for s in coff.symbols
        if s.section > 0
        and (s.name in (name, "_" + name) or s.name.startswith(f"?{name}@"))
    ]
    if len(matches) != 1:
        defined = ", ".join(s.name for s in coff.symbols if s.section > 0)
        raise LookupError(
            f"expected one symbol for {name!r}, found {len(matches)}. "
            f"Defined symbols: {defined}"
        )
    return matches[0]


def function_bytes(coff: Coff, symbol: Symbol) -> tuple[bytes, tuple[Reloc, ...]]:
    section = coff.sections[symbol.section - 1]
    start = symbol.value
    later = [
        s.value
        for s in coff.symbols
        if s.section == symbol.section and s.value > start and s.type == FUNCTION_TYPE
    ]
    end = min(later, default=len(section.data))
    relocs = tuple(
        Reloc(r.offset - start, r.symbol, r.type)
        for r in section.relocs
        if start <= r.offset < end
    )
    return section.data[start:end], relocs
