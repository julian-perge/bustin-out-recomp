from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REFS = Path("build/strings.tsv")
# These are the escapes tools/ghidra_scripts/ExportStringRefs.java writes.
ESCAPE = re.compile(r"\\(\\|t|n|r|u[0-9a-f]{4})")
SIMPLE = {"\\": "\\", "t": "\t", "n": "\n", "r": "\r"}


@dataclass(frozen=True)
class StringRef:
    address: int
    text: str


def unescape(field: str) -> str:
    return ESCAPE.sub(lambda m: SIMPLE.get(m[1]) or chr(int(m[1][1:], 16)), field)


def read_refs(path: Path) -> dict[int, list[StringRef]]:
    refs: dict[int, list[StringRef]] = {}
    for line in path.read_text().splitlines():
        function, address, text = line.split("\t")
        refs.setdefault(int(function, 16), []).append(
            StringRef(int(address, 16), unescape(text))
        )
    return refs
