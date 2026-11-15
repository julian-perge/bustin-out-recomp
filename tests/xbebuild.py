import struct

RETAIL_ENTRY_KEY = 0xA8FC57AB
HEADER_SIZE = 0x1000
CERT_OFF = 0x400
SECTION_HEADERS_OFF = 0x500
NAMES_OFF = 0x700
LIBRARIES_OFF = 0x800


def build_xbe(
    sections: list[tuple[str, int, bytes]],
    libraries: list[tuple[str, int]],
    title_id: int,
    entry: int,
    base: int = 0x10000,
) -> bytes:
    header = bytearray(HEADER_SIZE)
    header[0:4] = b"XBEH"
    struct.pack_into("<I", header, 0x104, base)
    struct.pack_into(
        "<III",
        header,
        0x118,
        base + CERT_OFF,
        len(sections),
        base + SECTION_HEADERS_OFF,
    )
    struct.pack_into("<I", header, 0x128, entry ^ RETAIL_ENTRY_KEY)
    struct.pack_into("<II", header, 0x160, len(libraries), base + LIBRARIES_OFF)
    struct.pack_into("<I", header, CERT_OFF + 0x8, title_id)

    body = bytearray()
    name_cursor = NAMES_OFF
    for i, (name, va, data) in enumerate(sections):
        raw_addr = HEADER_SIZE + len(body)
        encoded = name.encode("ascii") + b"\0"
        header[name_cursor : name_cursor + len(encoded)] = encoded
        struct.pack_into(
            "<6I",
            header,
            SECTION_HEADERS_OFF + i * 56,
            0,
            va,
            len(data),
            raw_addr,
            len(data),
            base + name_cursor,
        )
        name_cursor += len(encoded)
        body += data

    for i, (name, build) in enumerate(libraries):
        struct.pack_into(
            "<8sHHHH",
            header,
            LIBRARIES_OFF + i * 16,
            name.encode("ascii"),
            1,
            0,
            build,
            0,
        )
    return bytes(header + body)
