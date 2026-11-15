from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def files_containing(needle: bytes, paths: Iterable[Path]) -> list[Path]:
    return [p for p in paths if needle in p.read_bytes()]
