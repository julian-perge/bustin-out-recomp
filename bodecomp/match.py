from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

from bodecomp.cl import compile_cpp
from bodecomp.coff import FUNCTION_TYPE, Coff, Reloc, Symbol, function_bytes, parse
from bodecomp.split import UNITS, read_units
from bodecomp.symbols import Entry, read_symbols
from bodecomp.xbe import Xbe

SRC = Path("src")
# The M0 sources are flag experiments with placeholder names, scored by bodecomp.m0.
SKIP = (Path("src/m0"),)
FUNCTIONS = Path("config/functions.csv")
UNIT_DIR = Path("build/target/units")
TARGET_SYMBOLS = Path("build/target/symbols.tsv")
BUILD = Path("build/match")
XBE = Path("orig/default.xbe")
FLAGS = ("/O2", "/G7", "/arch:SSE", "/GX")
HEADER = ("address", "status", "source", "score", "detail")
BLOCKERS = (
    "source shape",
    "integer width",
    "register tie",
    "scheduling",
    "unclassified",
)
DIR32, REL32 = 0x6, 0x14
JUMP = 0xE9
PADDING = {0xCC, 0x90}
UNINITIALIZED = 0x80
EXECUTABLE = 0x20000000

ADDRESS_LINE = re.compile(r"^//\s*0x([0-9A-Fa-f]{8})\s*$")
PARKED_LINE = re.compile(r"^//\s*parked:\s*(.+?)\s*$")
GENERATED_LINE = re.compile(r"^//\s*generated:\s*(.*?)\s*$")
GENERATED_BODY = re.compile(r"0x([0-9A-Fa-f]{8})")
DECLARED_LINE = re.compile(r"^//\s*declared:\s*(.*?)\s*$")
DECLARED_BODY = re.compile(r"0x([0-9A-Fa-f]{8})\s+(.+)")
INCLUDE_LINE = re.compile(r'^\s*#\s*include\s*"([^"]+)"')
AUTO_ADDRESS = re.compile(r"^(?:FUN|DAT|LAB)_([0-9A-Fa-f]{8})$")
OPERATOR = re.compile(r"((?:\w+::)*)operator\s+(new|delete)\s*$")
OPERATOR_CODES = {"operator new": "??2", "operator delete": "??3"}
# libcmt.lib (exsup.obj) defines __except_list as the absolute value 0. It is
# the offset of the exception list in the thread block that FS points to, so
# the original holds a plain 0 there and has no relocation.
ABSOLUTE = {"__except_list": 0}


@dataclass(frozen=True)
class Marked:
    address: int
    source: Path
    name: str
    parked: str
    generated: bool = False


@dataclass(frozen=True)
class Declared:
    address: int
    name: str
    where: str


@dataclass(frozen=True)
class Result:
    address: int
    status: str
    source: Path
    score: str
    detail: str
    jump: int | None = None


class Unresolved(Exception):
    pass


def scan_source(path: Path, text: str) -> tuple[list[Marked], list[str]]:
    lines = text.splitlines()
    found, problems = [], []
    for i, line in enumerate(lines):
        if g := GENERATED_LINE.match(line.strip()):
            if body := GENERATED_BODY.fullmatch(g.group(1)):
                found.append(Marked(int(body.group(1), 16), path, "", "", True))
            else:
                problems.append(
                    f"{path}:{i + 1}: generated needs one 8-digit 0xADDRESS"
                )
            continue
        m = ADDRESS_LINE.match(line.strip())
        if not m:
            continue
        j = i + 1
        parked = ""
        if j < len(lines) and (p := PARKED_LINE.match(lines[j].strip())):
            parked = p.group(1)
            j += 1
            if parked not in BLOCKERS:
                problems.append(f"{path}:{j}: unknown blocker class {parked!r}")
        head = ""
        while j < len(lines) and "(" not in head:
            head += " " + lines[j]
            j += 1
        before = head.split("(")[0]
        if op := OPERATOR.search(before):
            name = f"{op.group(1)}operator {op.group(2)}"
        elif "operator" in before:
            name = ""
        else:
            name = before.split()[-1].lstrip("*&") if "(" in head else ""
        if not name:
            problems.append(f"{path}:{i + 1}: no function definition follows")
            continue
        found.append(Marked(int(m.group(1), 16), path, name, parked))
    return found, problems


def decorated_prefixes(name: str) -> tuple[str, ...]:
    parts = name.split("::")
    leaf, scopes = parts[-1], parts[:-1]
    scope = "".join(f"{s}@" for s in reversed(scopes))
    if leaf in OPERATOR_CODES:
        return (f"{OPERATOR_CODES[leaf]}{scope}@",)
    if scopes and leaf == scopes[-1]:
        return (f"??0{scope}@",)
    if scopes and leaf == "~" + scopes[-1]:
        return (f"??1{scope}@",)
    if scopes:
        return (f"?{leaf}@{scope}@",)
    return (f"?{leaf}@@", f"_{leaf}")


def read_declared(root: Path, source: Path) -> tuple[list[Declared], list[str]]:
    found, problems = [], []
    seen: set[Path] = set()
    queue = [source]
    while queue:
        path = queue.pop(0)
        if path in seen or not (root / path).is_file():
            continue
        seen.add(path)
        for i, line in enumerate((root / path).read_text().splitlines(), 1):
            if include := INCLUDE_LINE.match(line):
                # A quoted include is read from the folder of the file that
                # includes it, which is where VC71 looks first.
                queue.append(Path(os.path.normpath(path.parent / include.group(1))))
            if not (m := DECLARED_LINE.match(line.strip())):
                continue
            body = DECLARED_BODY.fullmatch(m.group(1))
            if not body:
                problems.append(
                    f"{path}:{i}: declared needs an 8-digit 0xADDRESS and a name"
                )
                continue
            prefix = decorated_prefixes(body.group(2))[0]
            member = "::" in body.group(2) and not prefix.startswith("??")
            if not (member or prefix.startswith(("??0", "??1"))):
                problems.append(
                    f"{path}:{i}: declared takes only a constructor, a destructor "
                    f"or a member function, not {body.group(2)}"
                )
            else:
                address = int(body.group(1), 16)
                found.append(Declared(address, body.group(2), f"{path}:{i}"))
    return found, problems


def _defines(symbol: str, prefix: str) -> bool:
    if prefix.startswith("_"):
        return symbol == prefix
    # VC71 names a vtordisp thunk after the function it jumps to, with a "$"
    # after the scope. The thunk is not the function's definition.
    return symbol.startswith(prefix) and not symbol.startswith(prefix + "$")


def defined_function(coff: Coff, name: str) -> Symbol:
    prefixes = decorated_prefixes(name)
    hits = [
        s
        for s in coff.symbols
        if s.section > 0
        and s.type == FUNCTION_TYPE
        and any(_defines(s.name, p) for p in prefixes)
    ]
    if len(hits) != 1:
        raise Unresolved(f"{len(hits)} compiled symbols for {name}")
    return hits[0]


def scope_path(decorated: str) -> str | None:
    if decorated.startswith("_") and not decorated.startswith("__"):
        return decorated[1:]
    if not decorated.startswith("?") or decorated.startswith("??"):
        return None
    names = decorated[1:].split("@@")[0].split("@")
    if not all(re.fullmatch(r"[A-Za-z_]\w*", n) for n in names):
        return None
    return "::".join(reversed(names))


class Resolver:
    def __init__(
        self,
        coff: Coff,
        addresses: dict[str, int],
        entries: list[Entry],
        xbe: Xbe,
        declared: dict[str, int] | None = None,
    ):
        self.coff = coff
        self.addresses = addresses
        self.xbe = xbe
        self.declared = declared or {}
        # Code without an address comment that a check compared with the
        # original, by the original address of its first byte. The value is
        # "" when a check that reached it passed, and the problem of the first
        # check that reached it when none passed.
        self.checked: dict[int, str] = {}
        # The address that such code jumps to, when it ends in a jump.
        self.jumps: dict[int, int] = {}
        self.by_name: dict[str, list[int]] = {}
        for e in entries:
            self.by_name.setdefault(e.name, []).append(e.address)

    def external(self, name: str) -> int:
        if name in ABSOLUTE:
            return ABSOLUTE[name]
        if name in self.by_name and len(self.by_name[name]) == 1:
            return self.by_name[name][0]
        for prefix, address in self.declared.items():
            if name.startswith(prefix):
                return address
        path = scope_path(name)
        leaf = path.split("::")[-1] if path else ""
        if m := AUTO_ADDRESS.match(leaf):
            return int(m.group(1), 16)
        hits = self.by_name.get(path, []) if path else []
        if len(hits) != 1:
            raise Unresolved(f"{name} names {len(hits)} entries in symbols.txt")
        return hits[0]

    def local_code(self, section: int, position: int) -> int | None:
        owners = [
            s
            for s in self.coff.symbols
            if s.section == section
            and s.type == FUNCTION_TYPE
            and s.value <= position
            and s.name in self.addresses
        ]
        if not owners:
            return None
        owner = max(owners, key=lambda s: s.value)
        return self.addresses[owner.name] + position - owner.value

    def local_bytes(self, section: int, position: int, value: int, seen: dict) -> None:
        sec = self.coff.sections[section - 1]
        if sec.characteristics & UNINITIALIZED:
            raise Unresolved(f"{sec.name} is uninitialized and cannot be checked")
        # A label inside generated code, such as the one VC71 puts on the last
        # instruction of an unwind funclet, does not end the item. Only the
        # next function does, so every byte of the funclet is compared.
        code = bool(sec.characteristics & EXECUTABLE)
        marks = sorted(
            {0, len(sec.data)}
            | {
                s.value
                for s in self.coff.symbols
                if s.section == section and (s.type == FUNCTION_TYPE or not code)
            }
        )
        start = max(m for m in marks if m <= position)
        end = min((m for m in marks if m > start), default=len(sec.data))
        address = value - (position - start)
        if (section, start) in seen:
            if seen[section, start] != address:
                raise Unresolved(
                    f"{sec.name} item at +0x{start:X} is expected at "
                    f"0x{seen[section, start]:08X} and 0x{address:08X}"
                )
            return
        seen[section, start] = address
        try:
            original = self.xbe.read(address, end - start)
        except ValueError as error:
            raise Unresolved(str(error)) from None
        item = sec.data[start:end]
        sites = set()
        # A relocation that points elsewhere does not end the walk. The items
        # behind the later relocations are still compared, so that a claimed
        # function among them counts as reached.
        problem = None
        for r in sec.relocs:
            if not start <= r.offset < end:
                continue
            at = r.offset - start
            sites.update(range(at, at + 4))
            literal = int.from_bytes(original[at : at + 4], "little", signed=True)
            expected = literal + (address + at + 4 if r.type == REL32 else 0)
            inplace = int.from_bytes(item[at : at + 4], "little", signed=True)
            last = at >= 1 and at + 4 == len(item)
            if code and last and r.type == REL32 and item[at - 1] == JUMP:
                self.jumps[address] = expected
            try:
                if self.value(r.symbol, inplace, expected, seen) != expected:
                    raise Unresolved(f"{sec.name}+0x{r.offset:X} points elsewhere")
            except Unresolved as error:
                problem = problem or error
        if problem:
            raise problem
        for i, (a, b) in enumerate(zip(item, original, strict=True)):
            if i not in sites and a != b:
                raise Unresolved(
                    f"{sec.name} item at +0x{start:X} differs from 0x{address:08X}"
                )

    def site(self, name: str, inplace: int, expected: int) -> int:
        seen: dict = {}
        failure = None
        try:
            value = self.value(name, inplace, expected, seen)
        except Unresolved as error:
            failure = error
        # The items of one check can refer to each other. A check that passes
        # proves each item it compared equal to the original, whatever another
        # check found. A check that fails proves none of them equal.
        for (section, _), address in seen.items():
            if not self.coff.sections[section - 1].characteristics & EXECUTABLE:
                continue
            if failure is None:
                self.checked[address] = ""
            else:
                self.checked.setdefault(address, str(failure))
        if failure:
            raise failure
        return value

    def value(self, name: str, inplace: int, expected: int | None, seen: dict) -> int:
        # coff.Reloc keeps the symbol's name, not its index, so two symbols
        # with one name (COMDAT section symbols) cannot be told apart.
        named = [s for s in self.coff.symbols if s.name == name]
        defined = [s for s in named if s.section > 0]
        if len(defined) == 1:
            named = defined
        if len(named) != 1:
            raise Unresolved(f"{len(named)} symbols are named {name}")
        symbol = named[0]
        if symbol.alias:
            return self.value(symbol.alias, inplace, expected, seen)
        if symbol.section <= 0:
            return self.external(name) + inplace
        position = symbol.value + inplace
        sec = self.coff.sections[symbol.section - 1]
        if sec.characteristics & EXECUTABLE:
            address = self.local_code(symbol.section, position)
            if address is not None:
                return address
            # Code without an address comment is code the compiler generated,
            # such as a deleting destructor, so its bytes and relocations are
            # checked against the original at the address the reference expects.
            if expected is None:
                raise Unresolved(
                    f"offset 0x{position:X} lies in no function with an address comment"
                )
        if expected is None:
            raise Unresolved(f"{name} has no original address to check against")
        self.local_bytes(symbol.section, position, expected, seen)
        return expected


def target_value(name: str, inplace: int, table: dict[str, int]) -> int:
    if m := AUTO_ADDRESS.match(name):
        return int(m.group(1), 16) + inplace
    if name not in table:
        raise Unresolved(f"target symbol {name} is not in symbols.tsv")
    return table[name] + inplace


def compare(
    address: int,
    unit: bytes,
    unit_relocs: tuple[Reloc, ...],
    built: bytes,
    built_relocs: tuple[Reloc, ...],
    resolver: Resolver,
    table: dict[str, int],
) -> tuple[str, str, str]:
    built = built.rstrip(b"\xcc")
    end = len(unit)
    while end > len(built) and unit[end - 1] in PADDING:
        end -= 1
    target = unit[:end]
    sites = {r.offset for r in unit_relocs} | {r.offset for r in built_relocs}
    problems = {}
    for o in sorted(sites):
        problem = _site(
            o, address, target, unit_relocs, built, built_relocs, resolver, table
        )
        if problem:
            problems[o] = problem
    # A relocation site's four bytes count as equal when both sides resolve
    # to the same address, whatever bytes the objects hold there.
    same = [
        i < len(target) and i < len(built) and target[i] == built[i]
        for i in range(max(len(target), len(built)))
    ]
    for o in sites:
        for i in range(o, min(o + 4, len(same))):
            same[i] = o not in problems
    if all(same):
        return "matched", "100.0", ""
    score = f"{100 * sum(same) / len(same):.1f}"
    diff = same.index(False)
    site = next((o for o in sorted(problems) if o <= diff < o + 4), None)
    if site is not None:
        detail = f"relocation at +0x{site:X}: {problems[site]}"
    else:
        detail = (
            f"first difference at +0x{diff:X}, "
            f"target {len(target)} bytes, built {len(built)} bytes"
        )
    return "nonmatching", score, detail


def _site(o, address, target, unit_relocs, built, built_relocs, resolver, table):
    t = next((r for r in unit_relocs if r.offset == o), None)
    b = next((r for r in built_relocs if r.offset == o), None)
    if b is None:
        return f"target relocates to {t.symbol}, built has none"
    if b.type not in (DIR32, REL32):
        return f"unsupported relocation type 0x{b.type:X}"
    if t is not None and t.type != b.type:
        return f"type 0x{b.type:X}, target 0x{t.type:X}"
    if o + 4 > len(target) or o + 4 > len(built):
        return "site runs past the end"
    literal = int.from_bytes(target[o : o + 4], "little", signed=True)
    try:
        if t is not None:
            expected = target_value(t.symbol, literal, table)
        elif b.type == REL32:
            expected = literal + address + o + 4
        else:
            expected = literal & 0xFFFFFFFF
        inplace = int.from_bytes(built[o : o + 4], "little", signed=True)
        got = resolver.site(b.symbol, inplace, expected)
    except Unresolved as error:
        return str(error)
    if got != expected:
        return f"built 0x{got & 0xFFFFFFFF:08X}, target 0x{expected & 0xFFFFFFFF:08X}"
    return None


def read_target_table(path: Path) -> dict[str, int]:
    table: dict[str, int] = {}
    for line in path.read_text().splitlines():
        address, _, _, name = line.split("\t", 3)
        table[name] = int(address, 16)
    return table


def scan(root: Path) -> tuple[list[Marked], list[str]]:
    marked, problems = [], []
    # Two sources can include one header, so its lines and problems are kept once.
    declared: dict[str, Declared] = {}
    misdeclared: dict[str, None] = {}
    for path in sorted((root / SRC).rglob("*.cpp")):
        rel = path.relative_to(root)
        if any(rel.is_relative_to(s) for s in SKIP):
            continue
        found, bad = scan_source(rel, path.read_text())
        marked += found
        problems += bad
        lines, bad = read_declared(root, rel)
        declared.update((d.where, d) for d in lines)
        misdeclared.update(dict.fromkeys(bad))
    seen: dict[int, Path] = {}
    for m in marked:
        if m.address in seen:
            problems.append(
                f"0x{m.address:08X} is claimed by {seen[m.address]} and {m.source}"
            )
        seen[m.address] = m.source
    problems += misdeclared
    first: dict[str, Declared] = {}
    for d in declared.values():
        other = first.setdefault(d.name, d)
        if other.address != d.address:
            problems.append(
                f"{d.name} is declared at 0x{other.address:08X} in {other.where} "
                f"and at 0x{d.address:08X} in {d.where}"
            )
    return marked, problems


def _first_error(log: str) -> str:
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    errors = [line for line in lines if "error" in line.lower()]
    return (errors or lines or [""])[0]


def run(
    root: Path, compile=compile_cpp, jobs: int | None = None
) -> tuple[list[Result], list[str]]:
    marked, problems = scan(root)
    if problems:
        return [], problems
    xbe = Xbe.parse((root / XBE).read_bytes())
    table = read_target_table(root / TARGET_SYMBOLS)
    entries = read_symbols(root / "config/symbols.txt")

    def check(source: Path) -> list[Result]:
        group = [m for m in marked if m.source == source]
        return check_source(root, source, group, xbe, table, entries, compile)

    # Nearly all of the time goes to the compiler, which runs as its own
    # process, so threads are enough to compile several sources at once.
    sources = sorted({m.source for m in marked})
    with ThreadPoolExecutor(max_workers=jobs or os.cpu_count()) as pool:
        results = [r for found in pool.map(check, sources) for r in found]
    return sorted(settle_jumps(results), key=lambda r: r.address), []


def settle_jumps(results: list[Result]) -> list[Result]:
    settled = list(results)
    # A thunk can jump to a claimed function that also ends in a jump. A row
    # that changes can change the row of a thunk before it, so the pass
    # repeats until no row changes.
    changed = True
    while changed:
        changed = False
        status = {r.address: r.status for r in settled}
        for i, r in enumerate(settled):
            if r.status != "matched" or r.jump is None:
                continue
            target = status.get(r.jump, "not claimed")
            if target != "matched":
                detail = f"its jump target 0x{r.jump:08X} is {target}"
                settled[i] = replace(r, status="nonmatching", detail=detail)
                changed = True
    return settled


def check_source(
    root: Path,
    source: Path,
    group: list[Marked],
    xbe: Xbe,
    table: dict[str, int],
    entries: list[Entry],
    compile=compile_cpp,
) -> list[Result]:
    output = BUILD / source.with_suffix(".obj")
    compiled = compile(root, source, output, FLAGS)
    if not compiled.ok:
        error = _first_error(compiled.log).replace(",", ";")
        return [
            Result(m.address, "error", source, "", f"compile: {error}") for m in group
        ]
    coff = parse((root / output).read_bytes())
    results = []
    symbols: dict[Marked, Symbol] = {}
    for m in group:
        if m.generated:
            continue
        try:
            symbols[m] = defined_function(coff, m.name)
        except Unresolved as error:
            results.append(Result(m.address, "error", source, "", str(error)))
    addresses = {s.name: m.address for m, s in symbols.items()}
    declared = {
        decorated_prefixes(d.name)[0]: d.address for d in read_declared(root, source)[0]
    }
    resolver = Resolver(coff, addresses, entries, xbe, declared)
    for m, symbol in symbols.items():
        unit_path = root / UNIT_DIR / f"{m.address:08X}.obj"
        if not unit_path.exists():
            results.append(
                Result(m.address, "error", source, "", "no target unit starts here")
            )
            continue
        unit = parse(unit_path.read_bytes()).sections[0]
        built, relocs = function_bytes(coff, symbol)
        status, score, detail = compare(
            m.address, unit.data, unit.relocs, built, relocs, resolver, table
        )
        if m.parked:
            status, detail = "parked", m.parked
        results.append(Result(m.address, status, source, score, detail))
    # The checks above reach compiler-generated code, so the claims come last.
    for m in group:
        if not m.generated:
            continue
        problem = resolver.checked.get(m.address)
        if problem is None:
            detail = "the check reached no compiler-generated function here"
            results.append(Result(m.address, "error", source, "", detail))
        elif problem:
            results.append(Result(m.address, "nonmatching", source, "", problem))
        else:
            jump = resolver.jumps.get(m.address)
            results.append(Result(m.address, "matched", source, "100.0", "", jump))
    return results


def render_csv(results: list[Result]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    for r in results:
        writer.writerow(
            [f"0x{r.address:08X}", r.status, r.source.as_posix(), r.score, r.detail]
        )
    return out.getvalue()


def read_functions(path: Path) -> dict[int, tuple[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        return {
            int(row["address"], 16): (row["status"], row["source"])
            for row in csv.DictReader(f)
        }


@dataclass(frozen=True)
class Candidate:
    address: int
    size: int
    relocs: int
    name: str


def candidates(
    root: Path, count: int, min_size: int, min_relocs: int = 0
) -> list[Candidate]:
    listed = read_functions(root / FUNCTIONS)
    game = {
        e.address: e.name
        for e in read_symbols(root / "config/symbols.txt")
        if e.kind == "function" and e.tier != "sdk" and e.address not in listed
    }
    sized = []
    for u in read_units(root / UNITS):
        if u.start not in game:
            continue
        unit = parse((root / UNIT_DIR / f"{u.start:08X}.obj").read_bytes())
        text = unit.sections[0]
        size = len(text.data.rstrip(b"\xcc\x90"))
        if size >= min_size and len(text.relocs) >= min_relocs:
            sized.append(Candidate(u.start, size, len(text.relocs), game[u.start]))
    sized.sort(key=lambda c: (c.relocs, c.size, c.address))
    return sized[:count]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.match")
    parser.add_argument(
        "--check", action="store_true", help="fail if config/functions.csv is stale"
    )
    sub = parser.add_subparsers(dest="command")
    pick = sub.add_parser("candidates", help="list unmatched game functions")
    pick.add_argument("count", type=int)
    pick.add_argument("--min-size", type=int, default=16)
    pick.add_argument("--min-relocs", type=int, default=0)
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "candidates":
        for c in candidates(root, args.count, args.min_size, args.min_relocs):
            print(f"0x{c.address:08X} {c.size:>5} bytes {c.relocs:>3} relocs {c.name}")
        return 0
    results, problems = run(root, compile=compile_cpp)
    for p in problems:
        print(p)
    if problems:
        return 1
    for r in results:
        line = f"0x{r.address:08X} {r.status:<11} {r.score:>5} {r.source.as_posix()}"
        print(line + (f"  {r.detail}" if r.detail else ""))
    counts = {
        s: sum(r.status == s for r in results)
        for s in ("matched", "nonmatching", "parked", "error")
    }
    print(", ".join(f"{n} {s}" for s, n in counts.items()))
    text = render_csv(results)
    path = root / FUNCTIONS
    if args.check:
        if not path.exists() or path.read_text() != text:
            print(f"{FUNCTIONS} is stale. Run: uv run python -m bodecomp.match")
            return 1
        return 0
    path.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
