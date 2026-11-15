from __future__ import annotations

import struct
from dataclasses import dataclass

RETAIL_ENTRY_KEY = 0xA8FC57AB


@dataclass(frozen=True)
class Section:
    name: str
    va: int
    vsize: int
    raw_addr: int
    raw_size: int


@dataclass(frozen=True)
class Library:
    name: str
    major: int
    minor: int
    build: int


@dataclass(frozen=True)
class Xbe:
    data: bytes
    base: int
    entry: int
    title_id: int
    sections: tuple[Section, ...]
    libraries: tuple[Library, ...]

    @classmethod
    def parse(cls, data: bytes) -> Xbe:
        if data[:4] != b"XBEH":
            raise ValueError("not an XBE file: the XBEH magic is missing")
        (base,) = struct.unpack_from("<I", data, 0x104)
        cert_va, section_count, sections_va = struct.unpack_from("<III", data, 0x118)
        (entry_encoded,) = struct.unpack_from("<I", data, 0x128)
        library_count, libraries_va = struct.unpack_from("<II", data, 0x160)
        (title_id,) = struct.unpack_from("<I", data, cert_va - base + 0x8)

        sections = []
        for i in range(section_count):
            _, va, vsize, raw_addr, raw_size, name_va = struct.unpack_from(
                "<6I", data, sections_va - base + i * 56
            )
            name_off = name_va - base
            name = data[name_off : data.index(b"\0", name_off)].decode("ascii")
            sections.append(Section(name, va, vsize, raw_addr, raw_size))

        libraries = []
        for i in range(library_count):
            raw_name, major, minor, build, _ = struct.unpack_from(
                "<8sHHHH", data, libraries_va - base + i * 16
            )
            name = raw_name.split(b"\0")[0].decode("ascii")
            libraries.append(Library(name, major, minor, build))

        return cls(
            data=data,
            base=base,
            entry=entry_encoded ^ RETAIL_ENTRY_KEY,
            title_id=title_id,
            sections=tuple(sections),
            libraries=tuple(libraries),
        )

    def read(self, va: int, size: int) -> bytes:
        for section in self.sections:
            if section.va <= va and va + size <= section.va + section.raw_size:
                start = section.raw_addr + (va - section.va)
                return self.data[start : start + size]
        raise ValueError(
            f"0x{va:08X}+{size} is not fully backed by file data in any section"
        )
