import struct

CODE = 0x60000020


def _name_field(name: str, strings: bytearray) -> bytes:
    raw = name.encode("ascii")
    if len(raw) <= 8:
        return raw.ljust(8, b"\0")
    offset = 4 + len(strings)
    strings += raw + b"\0"
    return struct.pack("<II", 0, offset)


def build_coff(sections, symbols) -> bytes:
    strings = bytearray()
    header_size = 20 + 40 * len(sections)
    cursor = header_size
    data_offsets = []
    sections = [tuple(s) + (CODE,) * (4 - len(s)) for s in sections]
    for _, data, _, _ in sections:
        data_offsets.append(cursor)
        cursor += len(data)
    reloc_offsets = []
    for _, _, relocs, _ in sections:
        reloc_offsets.append(cursor)
        cursor += 10 * len(relocs)
    symtab_offset = cursor
    symbols = [tuple(s) + (b"",) * (6 - len(s)) for s in symbols]
    records = sum(1 + len(aux) // 18 for *_, aux in symbols)

    out = bytearray(
        struct.pack("<HHIIIHH", 0x14C, len(sections), 0, symtab_offset, records, 0, 0)
    )
    for i, (name, data, relocs, characteristics) in enumerate(sections):
        out += name.encode("ascii").ljust(8, b"\0")
        out += struct.pack(
            "<IIIIIIHHI",
            0,
            0,
            len(data),
            data_offsets[i],
            reloc_offsets[i] if relocs else 0,
            0,
            len(relocs),
            0,
            characteristics,
        )
    for _, data, _, _ in sections:
        out += data
    for _, _, relocs, _ in sections:
        for offset, symbol_index, rtype in relocs:
            out += struct.pack("<IIH", offset, symbol_index, rtype)
    for name, value, section, stype, storage, aux in symbols:
        out += _name_field(name, strings)
        out += struct.pack("<IhHBB", value, section, stype, storage, len(aux) // 18)
        out += aux
    out += struct.pack("<I", 4 + len(strings)) + strings
    return bytes(out)
