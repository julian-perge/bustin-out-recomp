from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

from bodecomp.arlib import members
from bodecomp.coff import FUNCTION_TYPE, RELOC_WIDTHS, function_bytes, parse
from bodecomp.symbols import Entry, make_unique, read_symbols, write_symbols
from bodecomp.xbe import Xbe

MIN_SIZE_OUTSIDE_SDK = 16
PADDING = b"\xcc\x90"
SDK_SECTIONS = ("D3D", "XGRPH", "DSOUND", "XMV", "XPP")
# The two .text blocks where the XBE loader named dense runs of XAPI and CRT
# functions; see docs/m0-results.md, "How the 20 functions were chosen".
SDK_TEXT_BLOCKS = ((0x00100143, 0x0010AB91), (0x0021DF00, 0x00232C3F))
# The XBE header stamps each SDK library it was linked with; these are the
# matching file names in the XDK's xbox/lib folder.
STAMP_LIBS = {
    "XAPILIB": "xapilib.lib",
    "XBOXKRNL": "xboxkrnl.lib",
    "LIBCMT": "libcmt.lib",
    "LIBCPMT": "libcpmt.lib",
    "D3D8": "d3d8.lib",
    "XGRAPHC": "xgraphics.lib",
    "DSOUND": "dsound.lib",
    "XMV": "xmv.lib",
}


@dataclass(frozen=True)
class LibFunction:
    name: str
    lib: str
    member: str
    code: bytes
    mask: tuple[bool, ...]


def _is_i386_coff(data: bytes) -> bool:
    return len(data) >= 20 and data[:2] == b"\x4c\x01"


def lib_functions(lib_name: str, data: bytes) -> list[LibFunction]:
    out = []
    for member, body in members(data):
        if not _is_i386_coff(body):
            continue
        coff = parse(body)
        for symbol in coff.symbols:
            if symbol.section <= 0 or symbol.type != FUNCTION_TYPE:
                continue
            code, relocs = function_bytes(coff, symbol)
            mask = [True] * len(code)
            for r in relocs:
                for i in range(RELOC_WIDTHS.get(r.type, 4)):
                    if r.offset + i < len(mask):
                        mask[r.offset + i] = False
            out.append(LibFunction(symbol.name, lib_name, member, code, tuple(mask)))
    return out


def libs_for_stamps(stamps: list[str]) -> list[str]:
    unknown = [s for s in stamps if s not in STAMP_LIBS]
    if unknown:
        raise KeyError(f"no library file known for XBE stamps {unknown}")
    return [STAMP_LIBS[s] for s in stamps]


def _trimmed_length(f: LibFunction) -> int:
    length = len(f.code)
    while length > 0 and f.code[length - 1] in PADDING:
        length -= 1
    return length


def _equal(f: LibFunction, target: bytes) -> bool:
    return all(
        keep is False or a == b
        for a, b, keep in zip(f.code, target, f.mask, strict=False)
    )


def classify(
    entries: list[Entry],
    read: Callable[[int, int], bytes],
    functions: list[LibFunction],
    in_sdk: Callable[[int], bool],
    section_of: Callable[[int], str] = lambda address: "",
) -> list[Entry]:
    by_length: dict[int, list[LibFunction]] = defaultdict(list)
    for f in functions:
        by_length[len(f.code)].append(f)
        trimmed = _trimmed_length(f)
        if trimmed != len(f.code):
            by_length[trimmed].append(f)

    out = []
    for e in entries:
        if e.kind != "function" or e.size == 0:
            out.append(e)
            continue
        if e.size < MIN_SIZE_OUTSIDE_SDK and not in_sdk(e.address):
            out.append(e)
            continue
        target = read(e.address, e.size)
        hits = [f for f in by_length.get(e.size, []) if _equal(f, target)]
        names = sorted({f.name for f in hits})
        # An entry this match already named keeps its evidence, including a name
        # that make_unique suffixed with its address.
        own = (names[0], f"{names[0]}_{e.address:08X}") if names else ()
        if len(names) == 1 and e.name in own and e.evidence.startswith("lib:"):
            out.append(e)
        elif len(names) == 1:
            evidence = f"lib:{hits[0].lib}:{hits[0].member}"
            if e.tier != "auto" and e.name != names[0]:
                evidence += f"; was:{e.name}"
            out.append(replace(e, name=names[0], tier="sdk", evidence=evidence))
        elif names and in_sdk(e.address):
            # The count shows how many candidates there were when only five are listed.
            evidence = f"lib-ambiguous({len(names)}):" + ",".join(names[:5])
            out.append(replace(e, tier="sdk", evidence=evidence))
        elif section_of(e.address) in SDK_SECTIONS and e.tier == "auto":
            out.append(
                replace(e, tier="sdk", evidence=f"section:{section_of(e.address)}")
            )
        else:
            out.append(e)
    return make_unique(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Name SDK functions from XDK libs")
    parser.add_argument("--libs", type=Path, default=Path("tools/xdk/xbox/lib"))
    args = parser.parse_args(argv)

    xbe = Xbe.parse(Path("orig/default.xbe").read_bytes())
    functions = []
    for name in libs_for_stamps([lib.name for lib in xbe.libraries]):
        functions += lib_functions(name, (args.libs / name).read_bytes())

    def section_of(address: int) -> str:
        for s in xbe.sections:
            if s.va <= address < s.va + s.vsize:
                return s.name
        return ""

    def in_sdk(address: int) -> bool:
        return section_of(address) in SDK_SECTIONS or any(
            lo <= address < hi for lo, hi in SDK_TEXT_BLOCKS
        )

    symbols = Path("config/symbols.txt")
    before = read_symbols(symbols)
    after = classify(before, xbe.read, functions, in_sdk, section_of)
    write_symbols(symbols, after)
    named = sum(1 for e in after if e.evidence.startswith("lib:"))
    ambiguous = sum(1 for e in after if e.evidence.startswith("lib-ambiguous("))
    sections = sum(1 for e in after if e.evidence.startswith("section:"))
    print(
        f"{len(functions)} library functions; named {named}, ambiguous {ambiguous}, "
        f"section-only {sections}"
    )


if __name__ == "__main__":
    main()
