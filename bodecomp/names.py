from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

from bodecomp.match import FUNCTIONS, read_functions
from bodecomp.strings import REFS, StringRef, read_refs
from bodecomp.symbols import Entry, read_symbols, write_symbols
from bodecomp.sync import is_auto

SYMBOLS = Path("config/symbols.txt")
# A literal Class::Method name is allowed because sync cannot create Ghidra
# namespaces; ADR-0008 records why.
NAME = re.compile(r"^[A-Za-z_]\w*(?:::~?[A-Za-z_]\w*)*$")
EVIDENCE = re.compile(r"^(?:string|stated):0x[0-9A-F]{8}(?:,0x[0-9A-F]{8})*$")
# A matched name is the VC71 decorated name, or a plain C name (ADR-0011).
MATCHED_NAME = re.compile(r"^(?:\?\S+|[A-Za-z_]\w*)$")
SOURCE = re.compile(r"^src/\S+\.(?:c|cpp)$")
MATCHED_EVIDENCE = re.compile(r"^src/\S+\.(?:c|cpp)(?: was:\S+)?$")
STATED = re.compile(r"^([A-Za-z_]\w*(?:::~?[A-Za-z_]\w*)+)\(")
BATCH = 50


def cited(evidence: str) -> list[int]:
    return [int(a, 16) for a in evidence.split(":", 1)[1].split(",")]


def problems(entry: Entry, refs: dict[int, list[StringRef]]) -> list[str]:
    label = f"0x{entry.address:08X} {entry.name}"
    found = []
    if not NAME.match(entry.name) or is_auto(entry.name):
        found.append(f"{label}: {entry.name!r} is not a valid string-tier name")
    if not EVIDENCE.match(entry.evidence):
        found.append(
            f"{label}: evidence {entry.evidence!r} is not string: or stated: "
            "with string addresses"
        )
        return found
    have = {r.address for r in refs.get(entry.address, [])}
    for address in cited(entry.evidence):
        if address not in have:
            found.append(f"{label}: cites 0x{address:08X}, which it does not reference")
    return found


def matched_problems(entry: Entry, root: Path = Path(".")) -> list[str]:
    label = f"0x{entry.address:08X} {entry.name}"
    found = []
    if not MATCHED_NAME.match(entry.name) or is_auto(entry.name):
        found.append(f"{label}: {entry.name!r} is not a valid matched name")
    if not MATCHED_EVIDENCE.match(entry.evidence):
        found.append(
            f"{label}: evidence {entry.evidence!r} is not a src/ .c or .cpp path"
        )
        return found
    source = entry.evidence.split(" was:", 1)[0]
    if not (root / source).is_file():
        found.append(f"{label}: {source} does not exist")
    status, built_from = read_functions(root / FUNCTIONS).get(entry.address, ("", ""))
    if (status, built_from) != ("matched", source):
        found.append(f"{label}: {FUNCTIONS} does not list it as matched from {source}")
    return found


def _function(entries: list[Entry], address: int) -> Entry:
    for e in entries:
        if e.address == address and e.kind == "function":
            return e
    raise ValueError(f"0x{address:08X} is not a function in symbols.txt")


def set_name(
    entries: list[Entry],
    refs: dict[int, list[StringRef]],
    address: int,
    name: str,
    evidence: str,
    root: Path = Path("."),
) -> list[Entry]:
    target = _function(entries, address)
    matched = evidence.startswith("src/")
    allowed = ("auto", "gc", "string") if matched else ("auto", "string")
    if target.tier not in allowed:
        raise ValueError(
            f"0x{address:08X} {target.name} has tier {target.tier}; only "
            f"{', '.join(allowed)} names can be set with this evidence"
        )
    if any(e.name == name and e is not target for e in entries):
        raise ValueError(f"{name} is already used by another entry")
    if matched:
        if not SOURCE.match(evidence):
            raise ValueError(f"evidence {evidence!r} is not a src/ .c or .cpp path")
        if target.tier != "auto":
            evidence = f"{evidence} was:{target.name}"
        named = replace(target, name=name, tier="matched", evidence=evidence)
        found = matched_problems(named, root)
    else:
        named = replace(target, name=name, tier="string", evidence=evidence)
        found = problems(named, refs)
    if found:
        raise ValueError("; ".join(found))
    return [named if e is target else e for e in entries]


def clear_name(entries: list[Entry], address: int) -> list[Entry]:
    target = _function(entries, address)
    if target.tier != "string":
        raise ValueError(
            f"0x{address:08X} {target.name} has tier {target.tier}; only string "
            "names can be cleared"
        )
    cleared = replace(target, name=f"FUN_{address:08x}", tier="auto", evidence="")
    return [cleared if e is target else e for e in entries]


def check(
    entries: list[Entry], refs: dict[int, list[StringRef]], root: Path = Path(".")
) -> list[str]:
    found = [p for e in entries if e.tier == "string" for p in problems(e, refs)]
    matched = [e for e in entries if e.tier == "matched"]
    return found + [p for e in matched for p in matched_problems(e, root)]


def stated(
    entries: list[Entry], refs: dict[int, list[StringRef]]
) -> list[tuple[int, str, list[int]]]:
    found: dict[int, dict[str, set[int]]] = {}
    for function, strings in refs.items():
        for r in strings:
            match = STATED.match(r.text)
            if match:
                found.setdefault(function, {}).setdefault(match[1], set()).add(
                    r.address
                )
    # The same stated name in two functions can be a helper and an inlined copy
    # of it, so the string does not say which one carries the name.
    owners = Counter(name for names in found.values() for name in names)
    auto = {e.address for e in entries if e.kind == "function" and e.tier == "auto"}
    used = {e.name for e in entries}
    out = []
    for function, names in sorted(found.items()):
        if function not in auto or len(names) != 1:
            continue
        ((name, addresses),) = names.items()
        if owners[name] == 1 and name not in used:
            out.append((function, name, sorted(addresses)))
    return out


def batches(
    entries: list[Entry], refs: dict[int, list[StringRef]], size: int = BATCH
) -> list[list[Entry]]:
    # Named functions stay in their batch, so batch N lists the same functions
    # before and after a namer works on it.
    game = sorted(
        (
            e
            for e in entries
            if e.kind == "function" and e.tier != "sdk" and e.address in refs
        ),
        key=lambda e: e.address,
    )
    return [game[i : i + size] for i in range(0, len(game), size)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.names")
    parser.add_argument("--symbols", type=Path, default=SYMBOLS)
    parser.add_argument("--refs", type=Path, default=REFS)
    commands = parser.add_subparsers(dest="command", required=True)
    set_parser = commands.add_parser("set")
    set_parser.add_argument("address")
    set_parser.add_argument("name")
    set_parser.add_argument("evidence")
    clear_parser = commands.add_parser("clear")
    clear_parser.add_argument("address")
    commands.add_parser("check")
    commands.add_parser("stated")
    batch_parser = commands.add_parser("batch")
    batch_parser.add_argument("number", type=int)
    batch_parser.add_argument("--size", type=int, default=BATCH)
    args = parser.parse_args(argv)

    if not args.refs.exists():
        print(
            f"{args.refs} is missing; run tools/export-strings.sh first",
            file=sys.stderr,
        )
        return 1
    entries = read_symbols(args.symbols)
    refs = read_refs(args.refs)

    if args.command == "check":
        found = check(entries, refs)
        for line in found:
            print(line)
        named = Counter(e.tier for e in entries)
        print(
            f"{named['string']} string names, {named['matched']} matched names, "
            f"{len(found)} problems"
        )
        return 1 if found else 0

    if args.command == "batch":
        if args.size < 1:
            print("--size must be at least 1", file=sys.stderr)
            return 1
        groups = batches(entries, refs, args.size)
        if not 1 <= args.number <= len(groups):
            print(
                f"batch {args.number} does not exist; there are {len(groups)}",
                file=sys.stderr,
            )
            return 1
        print(f"batch {args.number} of {len(groups)}")
        for e in groups[args.number - 1]:
            print(f"0x{e.address:08X} {e.name} {e.tier}")
            for r in refs[e.address]:
                print(f"  0x{r.address:08X} {json.dumps(r.text)}")
        return 0

    if args.command == "stated":
        found = stated(entries, refs)
        try:
            for function, name, addresses in found:
                evidence = "stated:" + ",".join(f"0x{a:08X}" for a in addresses)
                entries = set_name(entries, refs, function, name, evidence)
                print(f"0x{function:08X} {name}")
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        write_symbols(args.symbols, entries)
        print(f"named {len(found)} functions from stated names; run sync apply")
        return 0

    try:
        if args.command == "set":
            entries = set_name(
                entries, refs, int(args.address, 16), args.name, args.evidence
            )
        else:
            entries = clear_name(entries, int(args.address, 16))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    write_symbols(args.symbols, entries)
    print(f"{args.command} 0x{int(args.address, 16):08X} done; run sync apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
