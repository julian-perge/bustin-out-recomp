import pytest

from bodecomp.symbols import Entry, make_unique, read_symbols, write_symbols


def fn(address, name, tier="auto", evidence=""):
    return Entry(address, "function", 16, name, tier, evidence)


def test_round_trip_keeps_odd_names(tmp_path):
    path = tmp_path / "symbols.txt"
    entries = [
        fn(0x11000, "FID_conflict:__ld12tod", "sdk", "xbe-loader"),
        fn(0x10F00, "operator new", "sdk", "lib:libcmt.lib:new.obj"),
        Entry(0x2E1C00, "data", 0, "NtCreateEvent", "sdk", "xbe-loader"),
    ]
    write_symbols(path, entries)
    assert read_symbols(path) == sorted(entries, key=lambda e: (e.address, e.kind))
    assert (
        path.read_text().splitlines()[0] == "address\tkind\tsize\tname\ttier\tevidence"
    )


def test_rejects_unknown_header(tmp_path):
    path = tmp_path / "symbols.txt"
    path.write_text("addr\tname\n")
    with pytest.raises(ValueError, match="header"):
        read_symbols(path)


def test_duplicates_get_address_suffix_after_the_first():
    out = make_unique(
        [fn(0x20000, "__stricmp", "sdk"), fn(0x10000, "__stricmp", "sdk")]
    )
    assert [e.name for e in out] == ["__stricmp", "__stricmp_00020000"]


def test_make_unique_is_idempotent():
    once = make_unique(
        [
            fn(0x1, "__stricmp", "sdk"),
            fn(0x2, "__stricmp", "sdk"),
            fn(0x3, "thunk_FUN_9"),
            fn(0x4, "thunk_FUN_9"),
        ]
    )
    assert make_unique(once) == once


def test_duplicated_auto_names_all_get_their_own_suffix():
    out = make_unique(
        [fn(0x20000, "thunk_FUN_001608d0"), fn(0x10000, "thunk_FUN_001608d0")]
    )
    assert [e.name for e in out] == [
        "thunk_FUN_001608d0_00010000",
        "thunk_FUN_001608d0_00020000",
    ]


def test_stacked_suffixes_on_auto_names_are_normalized():
    out = make_unique(
        [
            fn(0x7ECB0, "thunk_FUN_001608d0_00160910"),
            fn(0x160910, "thunk_FUN_001608d0_00160910_00160910"),
        ]
    )
    assert [e.name for e in out] == [
        "thunk_FUN_001608d0_0007ECB0",
        "thunk_FUN_001608d0_00160910",
    ]


def test_suffix_never_collides_with_an_existing_name():
    out = make_unique([fn(0x1, "a"), fn(0x2, "a"), fn(0x3, "a_00000002")])
    names = [e.name for e in out]
    assert len(set(names)) == 3
