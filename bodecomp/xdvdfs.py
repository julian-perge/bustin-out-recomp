from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

SECTOR = 2048
XGD1_PARTITION = 0x18300000
MAGIC = b"MICROSOFT*XBOX*MEDIA"


@dataclass(frozen=True)
class Entry:
    name: str
    sector: int
    size: int
    attributes: int


def root_entries(f: BinaryIO, partition: int = XGD1_PARTITION) -> list[Entry]:
    f.seek(partition + 32 * SECTOR)
    descriptor = f.read(28)
    if descriptor[:20] != MAGIC:
        raise ValueError(
            f"no XDVDFS volume descriptor at partition offset 0x{partition:X}"
        )
    root_sector, root_size = struct.unpack_from("<II", descriptor, 20)
    f.seek(partition + root_sector * SECTOR)
    table = f.read(root_size)

    entries = []
    pending = [0]
    visited = set()
    while pending:
        offset = pending.pop()
        if offset in visited:
            continue
        visited.add(offset)
        left, right, sector, size, attributes, name_len = struct.unpack_from(
            "<HHIIBB", table, offset
        )
        name = table[offset + 14 : offset + 14 + name_len].decode("ascii", "replace")
        entries.append(Entry(name, sector, size, attributes))
        for child in (left, right):
            if child not in (0, 0xFFFF):
                pending.append(child * 4)
    return entries


def extract(iso: Path, name: str, out: Path, partition: int = XGD1_PARTITION) -> int:
    with iso.open("rb") as f:
        for entry in root_entries(f, partition):
            if entry.name.lower() != name.lower():
                continue
            f.seek(partition + entry.sector * SECTOR)
            data = f.read(entry.size)
            if len(data) != entry.size:
                raise ValueError(f"{name} is truncated in {iso}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            return entry.size
    raise FileNotFoundError(f"{name} is not in the root directory of {iso}")
