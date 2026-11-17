import hashlib
from dataclasses import replace

import pytest

from bodecomp import sync
from bodecomp.symbols import Entry, read_symbols, write_symbols
from bodecomp.sync import (
    from_ghidra,
    is_auto,
    merge,
    named_in_ghidra,
    parse_global,
    renames,
)


def test_auto_names():
    assert is_auto("FUN_00011000")
    assert is_auto("thunk_FUN_001608d0")
    assert is_auto("DAT_002e21a8")
    assert not is_auto("CreateThread")
    assert is_auto("FID_conflict:_fread")


def test_parse_global_line():
    assert parse_global("NtCreateEvent @ 002e1c00 [Label] (pointer) xrefs=1") == (
        0x2E1C00,
        "NtCreateEvent",
    )
    assert (
        parse_global("xboxkrnl.exe @ NO ADDRESS [Library] (undefined) xrefs=0") is None
    )


def test_from_ghidra_assigns_tiers():
    entries = from_ghidra(
        [
            {"address": 0x11000, "name": "FUN_00011000", "size": 20},
            {"address": 0x100EA2, "name": "entry", "size": 114},
            {"address": 0x101D04, "name": "CloseHandle", "size": 30},
        ],
        [(0x2E1C00, "NtCreateEvent"), (0x2E3000, "DAT_002e3000")],
    )
    tiers = {e.name: (e.tier, e.evidence) for e in entries}
    assert tiers["FUN_00011000"] == ("auto", "")
    assert tiers["CloseHandle"] == ("sdk", "xbe-loader")
    assert tiers["entry"] == ("sdk", "xbe-loader")
    assert tiers["NtCreateEvent"] == ("sdk", "xbe-loader")
    assert "DAT_002e3000" not in tiers


def test_symbols_txt_owns_names_above_auto():
    ghidra = [Entry(0x11000, "function", 24, "FUN_00011000", "auto", "")]
    existing = [
        Entry(0x11000, "function", 20, "_atol", "sdk", "lib:libcmt.lib:atox.obj")
    ]
    assert merge(ghidra, existing) == [
        Entry(0x11000, "function", 24, "_atol", "sdk", "lib:libcmt.lib:atox.obj")
    ]


def test_ghidra_names_win_over_auto_entries():
    ghidra = [Entry(0x11000, "function", 20, "CreateThread", "sdk", "xbe-loader")]
    existing = [Entry(0x11000, "function", 20, "FUN_00011000", "auto", "")]
    assert merge(ghidra, existing)[0].name == "CreateThread"


def test_merge_drops_addresses_ghidra_no_longer_has():
    existing = [Entry(0x11000, "function", 20, "FUN_00011000", "auto", "")]
    assert merge([], existing) == []


def test_merge_keeps_a_named_data_entry_ghidra_does_not_list():
    label = Entry(0x2D9DC0, "data", 0, "g_DeviceType_MU", "sdk", "xbe-loader")
    function = Entry(0x11000, "function", 20, "CreateThread", "sdk", "lib:a")
    assert merge([], [label, function]) == [label]


def test_renames_lists_only_differences():
    ghidra = [
        Entry(0x1, "function", 4, "thunk_FUN_9", "auto", ""),
        Entry(0x2, "function", 4, "thunk_FUN_9", "auto", ""),
    ]
    wanted = [
        Entry(0x1, "function", 4, "thunk_FUN_9", "auto", ""),
        Entry(0x2, "function", 4, "thunk_FUN_9_00000002", "auto", ""),
    ]
    assert renames(ghidra, wanted) == [(0x2, "function", "thunk_FUN_9_00000002")]


def test_thunks_to_named_functions_get_their_own_name():
    entries = from_ghidra(
        [
            {"address": 0x10A2EC, "name": "XcSHAFinal", "size": 6, "is_thunk": True},
            {
                "address": 0x7ECB0,
                "name": "thunk_FUN_001608d0",
                "size": 5,
                "is_thunk": True,
            },
            {"address": 0x101D04, "name": "CloseHandle", "size": 30},
        ],
        [],
    )
    names = {e.address: (e.name, e.tier) for e in entries}
    assert names[0x10A2EC] == ("thunk_XcSHAFinal", "sdk")
    assert names[0x7ECB0] == ("thunk_FUN_001608d0", "auto")
    assert names[0x101D04] == ("CloseHandle", "sdk")


def test_renames_compare_against_the_raw_ghidra_name():
    functions = [
        {"address": 0x10A2EC, "name": "XcSHAFinal", "size": 6, "is_thunk": True}
    ]
    raw = from_ghidra(functions, [], normalize=False)
    wanted = from_ghidra(functions, [])
    assert renames(raw, wanted) == [(0x10A2EC, "function", "thunk_XcSHAFinal")]


def test_parse_data_item():
    from bodecomp.sync import parse_data_item

    assert parse_data_item({"label": "D3D__Device", "address": "00264950"}) == (
        0x264950,
        "D3D__Device",
    )
    assert parse_data_item({"label": None, "address": "00264954"}) is None


class FakeGhidra:
    """Functions and data labels that behave like Ghidra's. A thunk with no name
    of its own shows thunk_FUN_... while its target has a default name, and the
    target's name once the target is named. A label is listed only once it sits
    on defined data."""

    def __init__(self):
        self.names = {0x10: "FUN_00000010", 0x20: None}
        self.thunks = {0x20: 0x10}
        self.labels = {0x30: "g_Label"}
        self.defined = set()

    def name(self, address):
        own = self.names[address]
        if own is None:
            target = self.name(self.thunks[address])
            return "thunk_" + target if target.startswith("FUN_") else target
        return own

    def read(self):
        functions = [
            {
                "address": a,
                "name": self.name(a),
                "size": 5,
                "is_thunk": a in self.thunks,
            }
            for a in self.names
        ]
        globals_ = [(a, n) for a, n in self.labels.items() if a in self.defined]
        return from_ghidra(functions, globals_), from_ghidra(
            functions, globals_, normalize=False
        )

    def rename(self, address, kind, name):
        if kind == "function":
            self.names[address] = name
        else:
            self.labels[address] = name

    def define(self, address):
        self.defined.add(address)


def test_apply_repeats_until_thunk_names_settle():
    from bodecomp.sync import apply_names

    ghidra = FakeGhidra()
    wanted = [
        Entry(0x10, "function", 5, "CloseHandle", "sdk", "lib:x"),
        Entry(0x20, "function", 5, "thunk_FUN_00000010", "sdk", "lib-ambiguous:x"),
    ]
    renamed, missing = apply_names(wanted, ghidra.read, ghidra.rename, ghidra.define)
    assert ghidra.name(0x10) == "CloseHandle"
    assert ghidra.name(0x20) == "thunk_FUN_00000010"
    assert renamed == 2
    assert missing == []


def test_apply_defines_data_it_cannot_see_before_naming_it():
    from bodecomp.sync import apply_names

    ghidra = FakeGhidra()
    wanted = [Entry(0x30, "data", 0, "g_Label", "sdk", "xbe-loader")]
    renamed, missing = apply_names(wanted, ghidra.read, ghidra.rename, ghidra.define)
    assert ghidra.defined == {0x30}
    assert missing == []


def test_check_lists_ghidra_entries_missing_from_symbols():
    from bodecomp.sync import unlisted

    ghidra = [
        Entry(0x1, "function", 4, "FUN_00000001", "auto", ""),
        Entry(0x2, "function", 4, "FUN_00000002", "auto", ""),
    ]
    wanted = [Entry(0x1, "function", 4, "FUN_00000001", "auto", "")]
    assert unlisted(ghidra, wanted) == [ghidra[1]]


def test_named_in_ghidra_lists_functions_symbols_txt_has_as_auto():
    ghidra = [
        Entry(0x11000, "function", 20, "LoadTweaks", "sdk", "xbe-loader"),
        Entry(0x11100, "function", 8, "FUN_00011100", "auto", ""),
        Entry(0x11200, "function", 8, "CreateThread", "sdk", "xbe-loader"),
    ]
    existing = [
        Entry(0x11000, "function", 20, "FUN_00011000", "auto", ""),
        Entry(0x11100, "function", 8, "FUN_00011100", "auto", ""),
    ]
    assert named_in_ghidra(ghidra, existing) == [ghidra[0]]


def test_export_refuses_functions_named_only_in_ghidra(tmp_path, monkeypatch, capsys):
    symbols = tmp_path / "symbols.txt"
    existing = [Entry(0x11000, "function", 20, "FUN_00011000", "auto", "")]
    write_symbols(symbols, existing)
    named = [Entry(0x11000, "function", 20, "LoadTweaks", "sdk", "xbe-loader")]
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (named, named))

    def no_renames(changes):
        raise AssertionError("export renamed in Ghidra")

    monkeypatch.setattr(sync, "_apply", no_renames)
    with pytest.raises(SystemExit) as stop:
        sync.main(["export"])
    assert stop.value.code == 1
    assert "named in Ghidra only: 0x00011000 LoadTweaks" in capsys.readouterr().out
    assert read_symbols(symbols) == existing


def test_export_takes_ghidra_names_when_told_to(tmp_path, monkeypatch):
    symbols = tmp_path / "symbols.txt"
    write_symbols(symbols, [Entry(0x11000, "function", 20, "FUN_00011000", "auto", "")])
    named = [Entry(0x11000, "function", 20, "CreateThread", "sdk", "xbe-loader")]
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (named, named))
    monkeypatch.setattr(sync, "_apply", lambda changes: None)
    sync.main(["export", "--accept-ghidra-names"])
    assert read_symbols(symbols) == named


STAMP_ENTRIES = [
    Entry(0x10000, "data", 0, "XBE_FILE_HEADER_00010000", "sdk", "xbe-loader"),
    Entry(0x11000, "function", 20, "CreateThread", "sdk", "xbe-loader"),
    Entry(0x11100, "function", 8, "FUN_00011100", "auto", ""),
    Entry(0x12000, "data", 4, "g_count", "string", "read by function 0x11000"),
]


def test_check_with_no_difference_writes_the_stamp(tmp_path, monkeypatch):
    symbols = tmp_path / "symbols.txt"
    write_symbols(symbols, STAMP_ENTRIES)
    stamp = tmp_path / "ghidra" / ".sync-stamp"
    stamp.parent.mkdir()
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "STAMP", stamp)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (STAMP_ENTRIES, STAMP_ENTRIES))
    with pytest.raises(SystemExit) as stop:
        sync.main(["check"])
    assert stop.value.code == 0
    lines = symbols.read_bytes().splitlines(keepends=True)
    function_lines = b"".join(
        line for line in lines if line.split(b"\t")[1] == b"function"
    )
    assert function_lines.count(b"\n") == 2
    assert stamp.read_text() == (
        f"symbols {hashlib.sha256(symbols.read_bytes()).hexdigest()}\n"
        f"functions {hashlib.sha256(function_lines).hexdigest()}\n"
    )


def test_check_with_a_difference_leaves_the_stamp_alone(tmp_path, monkeypatch):
    symbols = tmp_path / "symbols.txt"
    write_symbols(symbols, STAMP_ENTRIES)
    stamp = tmp_path / "ghidra" / ".sync-stamp"
    stamp.parent.mkdir()
    stamp.write_text("symbols old\nfunctions old\n")
    renamed = [
        STAMP_ENTRIES[0],
        replace(STAMP_ENTRIES[1], name="OtherName"),
        STAMP_ENTRIES[2],
    ]
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "STAMP", stamp)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (renamed, renamed))
    with pytest.raises(SystemExit) as stop:
        sync.main(["check"])
    assert stop.value.code == 1
    assert stamp.read_text() == "symbols old\nfunctions old\n"


@pytest.mark.parametrize(
    "ghidra",
    [
        STAMP_ENTRIES[:2],
        [*STAMP_ENTRIES, Entry(0x11200, "function", 4, "FUN_00011200", "auto", "")],
    ],
    ids=["missing in Ghidra", "missing in symbols.txt"],
)
def test_check_with_a_difference_does_not_write_a_new_stamp(
    tmp_path, monkeypatch, ghidra
):
    symbols = tmp_path / "symbols.txt"
    write_symbols(symbols, STAMP_ENTRIES)
    stamp = tmp_path / "ghidra" / ".sync-stamp"
    stamp.parent.mkdir()
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "STAMP", stamp)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (ghidra, ghidra))
    with pytest.raises(SystemExit) as stop:
        sync.main(["check"])
    assert stop.value.code == 1
    assert not stamp.exists()


def test_check_without_a_ghidra_directory_keeps_its_exit_code(
    tmp_path, monkeypatch, capsys
):
    symbols = tmp_path / "symbols.txt"
    write_symbols(symbols, STAMP_ENTRIES)
    stamp = tmp_path / "ghidra" / ".sync-stamp"
    monkeypatch.setattr(sync, "SYMBOLS", symbols)
    monkeypatch.setattr(sync, "STAMP", stamp)
    monkeypatch.setattr(sync, "_ghidra_entries", lambda: (STAMP_ENTRIES, STAMP_ENTRIES))
    with pytest.raises(SystemExit) as stop:
        sync.main(["check"])
    assert stop.value.code == 0
    assert not stamp.exists()
    assert "could not write" in capsys.readouterr().out
