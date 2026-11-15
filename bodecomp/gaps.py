from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from bodecomp.symbols import read_symbols
from bodecomp.xbe import Xbe

PAD = 0xCC
ALIGN = 16
CANDIDATES = Path("build/target/candidates.txt")
STARTS = Path("build/target/starts.txt")


@dataclass(frozen=True)
class Gap:
    start: int
    end: int


@dataclass(frozen=True)
class Summary:
    gaps: int
    gap_bytes: int
    padding_gaps: int
    code_bytes: int
    largest: list[tuple[Gap, int]]


def find_gaps(
    text_start: int, text_end: int, functions: list[tuple[int, int]]
) -> list[Gap]:
    # A size in symbols.txt counts the addresses in a function's body, which
    # Ghidra can split into separate ranges, so a span that runs past the next
    # function start is cut there instead of hiding the code after it.
    ordered = sorted(functions)
    starts = [address for address, _ in ordered[1:]] + [text_end]
    gaps = []
    cursor = text_start
    for (address, size), next_start in zip(ordered, starts, strict=True):
        if address >= text_end or address + size <= text_start:
            continue
        if address > cursor:
            gaps.append(Gap(cursor, address))
        cursor = max(cursor, min(address + size, next_start, text_end))
    if cursor < text_end:
        gaps.append(Gap(cursor, text_end))
    return gaps


def candidates(text: bytes, va: int, gaps: list[Gap]) -> list[int]:
    found = []
    for gap in gaps:
        first = -(-gap.start // ALIGN) * ALIGN
        for address in range(first, gap.end, ALIGN):
            offset = address - va
            if offset > 0 and text[offset - 1] == PAD and text[offset] != PAD:
                found.append(address)
    return found


def summarize(text: bytes, va: int, gaps: list[Gap], top: int = 10) -> Summary:
    counted = []
    for gap in gaps:
        chunk = text[gap.start - va : gap.end - va]
        counted.append((gap, len(chunk) - chunk.count(PAD)))
    with_code = sorted((c for c in counted if c[1]), key=lambda c: (-c[1], c[0].start))
    return Summary(
        gaps=len(gaps),
        gap_bytes=sum(g.end - g.start for g in gaps),
        padding_gaps=sum(1 for _, code in counted if code == 0),
        code_bytes=sum(code for _, code in counted),
        largest=with_code[:top],
    )


def write_addresses(path: Path, addresses: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{a:08X}\n" for a in addresses))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.gaps")
    parser.add_argument("command", choices=("candidates", "starts", "report"))
    parser.add_argument("--xbe", type=Path, default=Path("orig/default.xbe"))
    parser.add_argument("--symbols", type=Path, default=Path("config/symbols.txt"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    functions = [e for e in read_symbols(args.symbols) if e.kind == "function"]

    if args.command == "starts":
        out = args.out or STARTS
        starts = sorted({e.address for e in functions})
        write_addresses(out, starts)
        print(f"wrote {len(starts)} function starts to {out}")
        return 0

    xbe = Xbe.parse(args.xbe.read_bytes())
    section = next(s for s in xbe.sections if s.name == ".text")
    text = xbe.read(section.va, section.raw_size)
    gaps = find_gaps(
        section.va,
        section.va + section.raw_size,
        [(e.address, e.size) for e in functions],
    )
    if args.command == "candidates":
        out = args.out or CANDIDATES
        found = candidates(text, section.va, gaps)
        write_addresses(out, found)
        print(f"wrote {len(found)} candidates from {len(gaps)} gaps to {out}")
        return 0

    s = summarize(text, section.va, gaps)
    print(
        f"gaps {s.gaps}, bytes {s.gap_bytes:,}, padding-only gaps {s.padding_gaps}, "
        f"non-padding bytes {s.code_bytes:,}"
    )
    for gap, code in s.largest:
        print(f"  0x{gap.start:08X}-0x{gap.end:08X} {code:,} non-padding bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
