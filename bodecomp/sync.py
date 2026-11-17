from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from bodecomp.symbols import Entry, make_unique, read_symbols, write_symbols

SYMBOLS = Path("config/symbols.txt")
STAMP = Path("ghidra/.sync-stamp")
AUTO_PREFIXES = (
    "FUN_",
    "thunk_FUN_",
    "DAT_",
    "PTR_",
    "LAB_",
    "s_",
    "u_",
    "switchD_",
    "caseD_",
    "switchdataD_",
    # Ghidra's own Function ID analysis picks one of several equal library
    # functions and marks the name, so it is no evidence of where code came from.
    "FID_conflict:",
)
GLOBAL_LINE = re.compile(r"^(?P<name>.+?) @ (?P<address>[0-9a-fA-F]{8}) \[")


def is_auto(name: str) -> bool:
    return name.startswith(AUTO_PREFIXES)


def parse_global(line: str) -> tuple[int, str] | None:
    match = GLOBAL_LINE.match(line)
    if not match:
        return None
    return int(match["address"], 16), match["name"]


def parse_data_item(item: dict) -> tuple[int, str] | None:
    if not item.get("label"):
        return None
    return int(item["address"], 16), item["label"]


def from_ghidra(
    functions: list[dict], globals_: list[tuple[int, str]], normalize: bool = True
) -> list[Entry]:
    entries = []
    for f in functions:
        name = f["name"]
        auto = is_auto(name)
        # A thunk with no name of its own shows its target's name, and for a
        # kernel import that collides with the import itself in delinked objects.
        if (
            normalize
            and f.get("is_thunk")
            and not auto
            and not name.startswith("thunk_")
        ):
            name = "thunk_" + name
        entries.append(
            Entry(
                f["address"],
                "function",
                f["size"],
                name,
                "auto" if auto else "sdk",
                "" if auto else "xbe-loader",
            )
        )
    for address, name in globals_:
        if not is_auto(name):
            entries.append(Entry(address, "data", 0, name, "sdk", "xbe-loader"))
    return entries


def merge(ghidra: list[Entry], existing: list[Entry]) -> list[Entry]:
    old = {(e.address, e.kind): e for e in existing}
    out = []
    for g in ghidra:
        o = old.get((g.address, g.kind))
        if o is None or o.tier == "auto":
            out.append(g)
        else:
            out.append(replace(o, size=g.size))
    # Ghidra lists a label only when it sits on defined data (F-0010), so a named
    # data entry that it does not list is kept; apply defines and names it again.
    # Functions are always listed, so one that Ghidra no longer has is dropped.
    listed = {(g.address, g.kind) for g in ghidra}
    out += [
        o
        for o in existing
        if o.kind == "data" and o.tier != "auto" and (o.address, o.kind) not in listed
    ]
    return make_unique(out)


def named_in_ghidra(ghidra: list[Entry], existing: list[Entry]) -> list[Entry]:
    old = {(e.address, e.kind): e for e in existing}
    out = []
    for g in ghidra:
        o = old.get((g.address, g.kind))
        if (
            g.kind == "function"
            and g.tier != "auto"
            and o is not None
            and o.tier == "auto"
        ):
            out.append(g)
    return out


def renames(ghidra: list[Entry], wanted: list[Entry]) -> list[tuple[int, str, str]]:
    current = {(e.address, e.kind): e.name for e in ghidra}
    return [
        (e.address, e.kind, e.name)
        for e in wanted
        if current.get((e.address, e.kind)) not in (None, e.name)
    ]


def unlisted(ghidra: list[Entry], wanted: list[Entry]) -> list[Entry]:
    known = {(e.address, e.kind) for e in wanted}
    return [e for e in ghidra if (e.address, e.kind) not in known]


def _ghidra_entries() -> tuple[list[Entry], list[Entry]]:
    from bodecomp import ghidra_api

    functions = ghidra_api.list_functions()
    globals_ = ghidra_api.list_named_globals()
    return (
        from_ghidra(functions, globals_),
        from_ghidra(functions, globals_, normalize=False),
    )


MAX_PASSES = 5


def apply_names(
    wanted: list[Entry],
    read: Callable[[], tuple[list[Entry], list[Entry]]],
    rename: Callable[[int, str, str], None],
    define: Callable[[int], None],
) -> tuple[int, list[Entry]]:
    ghidra, _ = read()
    have = {(e.address, e.kind) for e in ghidra}
    # Ghidra lists a label only when it sits on defined data, so a data entry it
    # does not list gets a one-byte undefined item first, without claiming a type.
    # If anything is already defined there, Ghidra refuses and the error stops the run.
    for e in wanted:
        if e.kind == "data" and (e.address, e.kind) not in have:
            define(e.address)
    # A thunk with no name of its own shows its target's name, so naming a target
    # can change a thunk name that already matched. Repeat until nothing changes.
    renamed = 0
    for _ in range(MAX_PASSES):
        ghidra, raw = read()
        changes = renames(raw, wanted)
        if not changes:
            break
        for address, kind, name in changes:
            rename(address, kind, name)
        renamed += len(changes)
    else:
        raise RuntimeError(f"names still differ after {MAX_PASSES} passes")
    have = {(e.address, e.kind) for e in ghidra}
    return renamed, [e for e in wanted if (e.address, e.kind) not in have]


def stamp_hashes(path: Path) -> dict[str, str]:
    """Return the SHA-256 of the whole file and of its `function` lines.

    The function hash covers those lines in file order, each with its line end,
    so it equals `awk -F'\\t' '$2 == "function"' FILE | sha256sum`.
    """
    data = path.read_bytes()
    functions = b"".join(
        line
        for line in data.splitlines(keepends=True)
        if line.split(b"\t")[1:2] == [b"function"]
    )
    return {
        "symbols": hashlib.sha256(data).hexdigest(),
        "functions": hashlib.sha256(functions).hexdigest(),
    }


def write_stamp(symbols: Path, stamp: Path) -> None:
    text = "".join(f"{key} {value}\n" for key, value in stamp_hashes(symbols).items())
    try:
        stamp.write_text(text)
    except OSError as error:
        print(f"could not write {stamp}: {error}")


def _apply(changes: list[tuple[int, str, str]]) -> None:
    from bodecomp import ghidra_api

    for address, kind, name in changes:
        ghidra_api.rename(address, kind, name)
    if changes:
        ghidra_api.save()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sync config/symbols.txt with Ghidra")
    parser.add_argument("command", choices=("export", "apply", "check"))
    parser.add_argument(
        "--accept-ghidra-names",
        action="store_true",
        help="record functions named only in Ghidra as SDK names",
    )
    args = parser.parse_args(argv)

    if args.command == "apply":
        from bodecomp import ghidra_api

        renamed, missing = apply_names(
            read_symbols(SYMBOLS),
            _ghidra_entries,
            ghidra_api.rename,
            ghidra_api.define_data,
        )
        ghidra_api.save()
        print(f"renamed {renamed} in Ghidra; {len(missing)} entries not found")
        return

    ghidra, raw = _ghidra_entries()
    if args.command == "export":
        existing = read_symbols(SYMBOLS) if SYMBOLS.exists() else []
        # A game name needs a tier and evidence, which only symbols.txt can hold,
        # so a function named in Ghidra alone stops the export before anything is
        # written or renamed (ADR-0008).
        unrecorded = named_in_ghidra(ghidra, existing)
        if unrecorded and not args.accept_ghidra_names:
            for e in unrecorded[:20]:
                print(f"named in Ghidra only: 0x{e.address:08X} {e.name}")
            print(
                f"{len(unrecorded)} functions are named in Ghidra but auto in "
                "symbols.txt. Record a game name with `uv run python -m "
                "bodecomp.names set`, or rerun with --accept-ghidra-names to "
                "take them as SDK names."
            )
            sys.exit(1)
        wanted = merge(ghidra, existing)
        write_symbols(SYMBOLS, wanted)
        changes = renames(raw, wanted)
        _apply(changes)
        print(f"wrote {len(wanted)} entries, renamed {len(changes)} in Ghidra")
        return

    wanted = read_symbols(SYMBOLS)
    changes = renames(raw, wanted)
    have = {(e.address, e.kind) for e in ghidra}
    missing = [e for e in wanted if (e.address, e.kind) not in have]
    extra = unlisted(ghidra, wanted)
    for address, kind, name in changes[:20]:
        print(f"differs: 0x{address:08X} {kind} should be {name}")
    for e in missing[:20]:
        print(f"missing in Ghidra: 0x{e.address:08X} {e.kind} {e.name}")
    for e in extra[:20]:
        print(f"missing in symbols.txt: 0x{e.address:08X} {e.kind} {e.name}")
    print(
        f"{len(changes)} name differences, {len(missing)} missing, "
        f"{len(extra)} not in symbols.txt"
    )
    if changes or missing or extra:
        sys.exit(1)
    write_stamp(SYMBOLS, STAMP)
    sys.exit(0)


if __name__ == "__main__":
    main()
