from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from bodecomp.cl import compile_cpp
from bodecomp.coff import Reloc, parse
from bodecomp.ledger import GAME, status
from bodecomp.match import (
    FUNCTIONS,
    TARGET_SYMBOLS,
    UNIT_DIR,
    XBE,
    Unresolved,
    check_source,
    read_target_table,
    render_csv,
    run,
    scan,
    scan_source,
    target_value,
)
from bodecomp.split import UNITS, read_units
from bodecomp.strings import REFS, read_refs
from bodecomp.symbols import read_symbols
from bodecomp.xbe import Xbe

PADDING = b"\xcc\x90"
TRIVIAL = Path("src/game/trivial")
SCRATCH = Path("build/trivial")
MAX_SIZE = 16


@dataclass(frozen=True)
class Generated:
    address: int
    shape: str
    decls: tuple[str, ...]
    code: str


def masked(data: bytes, relocs: tuple[Reloc, ...]) -> str:
    text = data.rstrip(PADDING).hex()
    for r in relocs:
        text = text[: 2 * r.offset] + "R" * 8 + text[2 * r.offset + 8 :]
    return text


def _le(hex_: str, signed: bool = False) -> int:
    return int.from_bytes(bytes.fromhex(hex_), "little", signed=signed)


def _args(hex_: str) -> str | None:
    pop = _le(hex_)
    if pop == 0 or pop % 4:
        return None
    return ", ".join(f"int a{i}" for i in range(1, pop // 4 + 1))


def _code(address: int, signature: str, body: str = "") -> str:
    inner = f"    {body}\n" if body else ""
    return f"// 0x{address:08X}\n{signature}\n{{\n{inner}}}\n"


def _struct(address: int, method: str, offset: int | None = None) -> str:
    fields = []
    if offset:
        fields.append(f"    char pad[0x{offset:X}];\n")
    if offset is not None:
        fields.append("    int f;\n")
    return f"struct S_{address:08X}\n{{\n{''.join(fields)}    {method};\n}};"


def _target(data: bytes, relocs: tuple[Reloc, ...], table: dict[str, int]) -> int:
    (r,) = relocs
    literal = int.from_bytes(data[r.offset : r.offset + 4], "little", signed=True)
    return target_value(r.symbol, literal, table) & 0xFFFFFFFF


def _global(data: bytes, relocs: tuple[Reloc, ...], table: dict[str, int]) -> str:
    return f"DAT_{_target(data, relocs, table):08X}"


def c_string(text: bytes) -> str:
    out = []
    for b in text:
        if b in b'"\\?':
            out.append("\\" + chr(b))
        elif 0x20 <= b < 0x7F:
            out.append(chr(b))
        else:
            out.append(f"\\{b:03o}")
    return '"' + "".join(out) + '"'


def _delete_this(address: int, slot: int) -> str:
    s = f"S_{address:08X}"
    virtuals = "".join(f"    virtual void v{i}();\n" for i in range(slot))
    return (
        f"struct {s}\n{{\n{virtuals}    virtual ~{s}();\n"
        f"    void FUN_{address:08X}();\n}};"
    )


def recognise(
    address: int,
    data: bytes,
    relocs: tuple[Reloc, ...],
    table: dict[str, int],
    literals: dict[int, bytes] | None = None,
) -> Generated | None:
    pattern = masked(data, relocs)
    x = f"{address:08X}"
    fun, s = f"FUN_{x}", f"S_{x}"

    def done(shape, decls, signature, body=""):
        return Generated(address, shape, tuple(decls), _code(address, signature, body))

    if pattern == "c3":
        return done("empty", [], f"void {fun}()")
    if m := re.fullmatch(r"c2(....)", pattern):
        if (args := _args(m.group(1))) is None:
            return None
        decl = _struct(address, f"void {fun}({args})")
        return done("empty-args", [decl], f"void {s}::{fun}({args})")
    if pattern == "33c0c3":
        return done("zero", [], f"int {fun}()", "return 0;")
    if pattern == "32c0c3":
        return done("false", [], f"bool {fun}()", "return false;")
    if pattern == "b001c3":
        return done("true", [], f"bool {fun}()", "return true;")
    if m := re.fullmatch(r"b8([0-9a-f]{8})c3", pattern):
        value = _le(m.group(1), signed=True)
        return done("const", [], f"int {fun}()", f"return {value};")
    if pattern == "8bc1c3":
        decl = _struct(address, f"{s}* {fun}()")
        return done("this", [decl], f"{s}* {s}::{fun}()", "return this;")
    if m := re.fullmatch(r"8bc1c2(....)", pattern):
        if (args := _args(m.group(1))) is None:
            return None
        decl = _struct(address, f"{s}* {fun}({args})")
        return done("this-args", [decl], f"{s}* {s}::{fun}({args})", "return this;")
    offset = None
    if pattern == "8b01c3":
        offset = 0
    elif m := re.fullmatch(r"8b(?:41([0-9a-f]{2})|81([0-9a-f]{8}))c3", pattern):
        offset = _le(m.group(1) or m.group(2), signed=True)
    if offset is not None:
        if offset < 0:
            return None
        decl = _struct(address, f"int {fun}()", offset)
        return done("get", [decl], f"int {s}::{fun}()", "return f;")
    if pattern == "8b442404c3":
        return done("arg", [], f"int {fun}(int a1)", "return a1;")
    if pattern == "8bc18b4c24088908c20800":
        decl = _struct(address, f"{s}* {fun}(int a1, int a2)", 0)
        body = "f = a2;\n    return this;"
        return done("set-second-arg", [decl], f"{s}* {s}::{fun}(int a1, int a2)", body)
    if pattern == "8b0185c074048b40fcc333c0c3":
        decl = f"struct {s}\n{{\n    int* p;\n    int {fun}();\n}};"
        body = "return p ? p[-1] : 0;"
        return done("array-count", [decl], f"int {s}::{fun}()", body)
    if m := re.fullmatch(r"85c974078b016a01ff50([0-9a-f]{2})c3", pattern):
        disp = int(m.group(1), 16)
        if disp % 4 or disp >= 0x80:
            return None
        decl = _delete_this(address, disp // 4)
        return done("delete-this", [decl], f"void {s}::{fun}()", "delete this;")
    if pattern == "c701RRRRRRRRc3":
        decl = f"struct {s}\n{{\n    virtual ~{s}();\n}};"
        return done("vtable-destructor", [decl], f"{s}::~{s}()")
    if pattern == "8bc1c700RRRRRRRRc3":
        decl = f"struct {s}\n{{\n    {s}();\n    virtual ~{s}() {{}}\n}};"
        return done("vtable-constructor", [decl], f"{s}::{s}()")
    calls = {
        "e9RRRRRRRR": "jump",
        "ff25RRRRRRRR": "jump-pointer",
        "8b4c2404e9RRRRRRRR": "forward-member",
        "b8RRRRRRRRc3": "global-address",
    }
    if pattern in calls:
        try:
            target = _target(data, relocs, table)
        except Unresolved:
            return None
        shape, t = calls[pattern], f"{target:08X}"
        if shape == "jump":
            return done(shape, [f"void FUN_{t}();"], f"void {fun}()", f"FUN_{t}();")
        if shape == "jump-pointer":
            decl = f"extern void (*DAT_{t})();"
            return done(shape, [decl], f"void {fun}()", f"DAT_{t}();")
        if shape == "forward-member":
            decl = f"struct {s}\n{{\n    void FUN_{t}();\n}};"
            body = f"a1->FUN_{t}();"
            return done(shape, [decl], f"void {fun}({s}* a1)", body)
        if target in (literals or {}):
            body = f"return {c_string(literals[target])};"
            return done("string-literal", [], f"const char* {fun}()", body)
        decl = f"extern char DAT_{t}[];"
        return done(shape, [decl], f"char* {fun}()", f"return DAT_{t};")
    globals_ = {
        "a1RRRRRRRRc3": ("global", "int", "int {fun}()", "return {g};"),
        "66a1RRRRRRRRc3": ("global16", "short", "short {fun}()", "return {g};"),
        "8b442404a3RRRRRRRRc3": (
            "set-global",
            "int",
            "void {fun}(int a1)",
            "{g} = a1;",
        ),
    }
    if pattern in globals_:
        shape, type_, signature, body = globals_[pattern]
        try:
            g = _global(data, relocs, table)
        except Unresolved:
            return None
        return done(
            shape,
            [f"extern {type_} {g};"],
            signature.format(fun=fun),
            body.format(g=g),
        )
    return None


DECLARED = re.compile(r"\b((?:FUN|DAT)_[0-9A-F]{8})\b")


def drop_conflicts(generated: list[Generated]) -> list[Generated]:
    """Drop functions whose declarations would clash in one scratch file.

    A free declaration of a function the same file defines would either
    conflict with its definition or let VC71 inline the call (F-0073), and
    two declarations of one global with different types do not compile.
    """
    defined = {
        name
        for g in generated
        if (name := f"FUN_{g.address:08X}") in g.code.splitlines()[1]
    }
    seen: dict[str, str] = {}
    kept = []
    for g in generated:
        free = [
            (m[1], d)
            for d in g.decls
            if not d.startswith("struct")
            if (m := DECLARED.search(d))
        ]
        if any(name in defined or seen.get(name, d) != d for name, d in free):
            continue
        seen.update(free)
        kept.append(g)
    return kept


def _small_units(
    root: Path, max_size: int
) -> tuple[list[tuple[int, bytes, tuple[Reloc, ...]]], list[str]]:
    marked, problems = scan(root)
    claimed = {m.address for m in marked if not m.source.is_relative_to(TRIVIAL)}
    generated = {m.address for m in marked if m.source.is_relative_to(TRIVIAL)}
    # A hand-written claim on a generated function is not a problem here,
    # because this run rewrites src/game/trivial/ without that function.
    replaced = {f"0x{a:08X} is claimed by" for a in claimed & generated}
    problems = [p for p in problems if not p.startswith(tuple(replaced))]
    if problems:
        return [], problems
    game = {
        e.address
        for e in read_symbols(root / "config/symbols.txt")
        if e.kind == "function" and status(e) in dict(GAME).values()
    }
    small = []
    for u in read_units(root / UNITS):
        if u.start not in game or u.start in claimed:
            continue
        text = parse((root / UNIT_DIR / f"{u.start:08X}.obj").read_bytes()).sections[0]
        if len(text.data.rstrip(PADDING)) <= max_size:
            small.append((u.start, text.data, text.relocs))
    return small, []


def read_literals(path: Path, xbe: Xbe) -> dict[int, bytes]:
    """Map each exported string address to its bytes, when the export is exact.

    The export decodes text, so a string is used as a literal only when its
    text encodes back to the bytes in the xbe up to the terminating NUL.
    """
    literals = {}
    for refs in read_refs(path).values():
        for ref in refs:
            text = ref.text.encode("latin-1", "replace")
            try:
                stored = xbe.read(ref.address, len(text) + 1)
            except ValueError:
                continue
            if stored == text + b"\0":
                literals[ref.address] = text
    return literals


def render_block(generated: list[Generated]) -> str:
    decls = dict.fromkeys(d for g in generated for d in g.decls)
    return "\n".join(decls) + "\n\n" + "\n".join(g.code for g in generated)


def generate(
    root: Path, max_size: int = MAX_SIZE, compile=compile_cpp
) -> tuple[dict[str, int], dict[str, int], list[str]]:
    small, problems = _small_units(root, max_size)
    if problems:
        return {}, {}, problems
    if not (root / REFS).exists():
        return {}, {}, [f"{REFS} is missing; run tools/export-strings.sh"]
    table = read_target_table(root / TARGET_SYMBOLS)
    xbe = Xbe.parse((root / XBE).read_bytes())
    literals = read_literals(root / REFS, xbe)
    blocks: dict[int, list[Generated]] = {}
    for address, data, relocs in small:
        if g := recognise(address, data, relocs, table, literals):
            blocks.setdefault(address >> 16, []).append(g)
    blocks = {b: drop_conflicts(gs) for b, gs in blocks.items()}
    entries = read_symbols(root / "config/symbols.txt")
    tried: Counter[str] = Counter()
    kept: Counter[str] = Counter()
    keep: dict[int, list[Generated]] = {}
    for block, generated in sorted(blocks.items()):
        source = SCRATCH / f"{block:04X}.cpp"
        (root / source).parent.mkdir(parents=True, exist_ok=True)
        text = render_block(generated)
        (root / source).write_text(text)
        group, _ = scan_source(source, text)
        results = check_source(root, source, group, xbe, table, entries, compile)
        if any(r.detail.startswith("compile: ") for r in results):
            error = results[0].detail.removeprefix("compile: ")
            return {}, {}, [f"{block:04X}: {error}"]
        matched = {r.address for r in results if r.status == "matched"}
        for g in generated:
            tried[g.shape] += 1
            kept[g.shape] += g.address in matched
        keep[block] = [g for g in generated if g.address in matched]
    if (root / TRIVIAL).exists():
        shutil.rmtree(root / TRIVIAL)
    for block, generated in keep.items():
        if generated:
            (root / TRIVIAL).mkdir(parents=True, exist_ok=True)
            (root / TRIVIAL / f"{block:04X}.cpp").write_text(render_block(generated))
    results, problems = run(root, compile)
    if problems:
        return dict(kept), dict(tried), problems
    (root / FUNCTIONS).write_text(render_csv(results))
    return dict(kept), dict(tried), []


def shapes(
    root: Path, count: int, max_size: int = MAX_SIZE
) -> list[tuple[str, int, str]]:
    small, problems = _small_units(root, max_size)
    if problems:
        raise SystemExit("\n".join(problems))
    marked, _ = scan(root)
    listed = {m.address for m in marked}
    table = read_target_table(root / TARGET_SYMBOLS)
    counts: Counter[str] = Counter()
    claim: dict[str, str] = {}
    for address, data, relocs in small:
        if address in listed:
            continue
        pattern = masked(data, relocs)
        counts[pattern] += 1
        if pattern not in claim:
            g = recognise(address, data, relocs, table)
            claim[pattern] = g.shape if g else "-"
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [(p, n, claim[p]) for p, n in ranked[:count]]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.trivial")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="write the trivial functions that match")
    gen.add_argument("--max-size", type=int, default=MAX_SIZE)
    top = sub.add_parser("shapes", help="list common patterns of small functions")
    top.add_argument("count", type=int, nargs="?", default=20)
    top.add_argument("--max-size", type=int, default=MAX_SIZE)
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "shapes":
        for pattern, n, shape in shapes(root, args.count, args.max_size):
            print(f"{n:>6} {pattern:<24} {shape}")
        return 0
    kept, tried, problems = generate(root, args.max_size)
    for shape, n in sorted(tried.items(), key=lambda item: -item[1]):
        print(f"{shape:<12} {kept.get(shape, 0)}/{n}")
    print(f"{'total':<12} {sum(kept.values())}/{sum(tried.values())}")
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
