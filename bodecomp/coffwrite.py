from __future__ import annotations

import struct

from bodecomp.coff import CoffSection, Symbol

I386 = 0x14C


def write_coff(sections: list[CoffSection], symbols: list[Symbol]) -> bytes:
    index: dict[str, int] = {}
    for i, symbol in enumerate(symbols):
        index.setdefault(symbol.name, i)
    for section in sections:
        for reloc in section.relocs:
            if reloc.symbol not in index:
                raise KeyError(f"relocation refers to unknown symbol {reloc.symbol!r}")

    strings = bytearray()

    def name_field(name: str) -> bytes:
        raw = name.encode("latin-1")
        if len(raw) <= 8:
            return raw.ljust(8, b"\0")
        offset = 4 + len(strings)
        strings.extend(raw + b"\0")
        return struct.pack("<II", 0, offset)

    cursor = 20 + 40 * len(sections)
    data_offsets, reloc_offsets = [], []
    for section in sections:
        data_offsets.append(cursor)
        cursor += len(section.data)
    for section in sections:
        reloc_offsets.append(cursor)
        cursor += 10 * len(section.relocs)
    symtab_offset = cursor

    out = bytearray(
        struct.pack(
            "<HHIIIHH", I386, len(sections), 0, symtab_offset, len(symbols), 0, 0
        )
    )
    for i, section in enumerate(sections):
        out += section.name.encode("ascii").ljust(8, b"\0")
        out += struct.pack(
            "<IIIIIIHHI",
            0,
            0,
            len(section.data),
            data_offsets[i],
            reloc_offsets[i] if section.relocs else 0,
            0,
            len(section.relocs),
            0,
            section.characteristics,
        )
    for section in sections:
        out += section.data
    for section in sections:
        for reloc in section.relocs:
            out += struct.pack("<IIH", reloc.offset, index[reloc.symbol], reloc.type)
    for symbol in symbols:
        out += name_field(symbol.name)
        out += struct.pack(
            "<IhHBB",
            symbol.value,
            symbol.section,
            symbol.type,
            symbol.storage_class,
            0,
        )
    out += struct.pack("<I", 4 + len(strings)) + strings
    return bytes(out)
