from bodecomp.coff import CoffSection, Reloc, Symbol, parse
from bodecomp.coffwrite import write_coff
from bodecomp.relink import relink, resolve, unit_problems
from bodecomp.split import Unit

CODE = 0x60000020
TEXT_VA = 0x11000


def unit(data, relocs, symbols):
    return parse(write_coff([CoffSection(".text", data, tuple(relocs), CODE)], symbols))


def test_resolve_prefers_table_then_address_suffix():
    assert resolve("_atol", {"_atol": 0x21E000}) == 0x21E000
    assert resolve("DAT_002e21a8", {}) == 0x2E21A8
    assert resolve("_atol", {}) is None


def test_relink_reproduces_dir32_and_rel32():
    original = b"\xe8\x03\x00\x00\x00\xc3\xcc\xcc" + b"\xa1\xa8\x21\x2e\x00\xc3"
    first = unit(
        b"\xe8\x00\x00\x00\x00\xc3\xcc\xcc",
        [Reloc(1, "FUN_00011008", 0x14)],
        [Symbol("FUN_00011000", 0, 1, 0x20, 2), Symbol("FUN_00011008", 0, 0, 0, 2)],
    )
    second = unit(
        b"\xa1\x00\x00\x00\x00\xc3",
        [Reloc(1, "DAT_002e21a8", 6)],
        [Symbol("FUN_00011008", 0, 1, 0x20, 2), Symbol("DAT_002e21a8", 0, 0, 0, 2)],
    )
    report = relink([(0x11000, first), (0x11008, second)], {}, original, TEXT_VA)
    assert report.ok
    assert report.mismatches == []


def test_unresolved_name_is_reported_and_fails():
    original = b"\xa1\x00\x10\x00\x00\xc3"
    only = unit(
        b"\xa1\x00\x00\x00\x00\xc3",
        [Reloc(1, "_g_secret", 6)],
        [Symbol("FUN_00011000", 0, 1, 0x20, 2), Symbol("_g_secret", 0, 0, 0, 2)],
    )
    report = relink([(0x11000, only)], {}, original, TEXT_VA)
    assert not report.ok
    assert report.unresolved == {"_g_secret": 1}


def test_byte_difference_is_reported_by_address():
    original = b"\x90\x90\xc3"
    only = unit(b"\x90\x91\xc3", [], [Symbol("FUN_00011000", 0, 1, 0x20, 2)])
    report = relink([(0x11000, only)], {}, original, TEXT_VA)
    assert report.mismatches == [0x11001]


def test_a_unit_resolves_its_own_symbols_first():
    # A jump table inside the unit refers to the unit's own case label.
    original = b"\x90\x90\x90\x90" + (0x11004).to_bytes(4, "little")
    only = unit(
        b"\x90\x90\x90\x90\x00\x00\x00\x00",
        [Reloc(4, "caseD_0", 6)],
        [Symbol("FUN_00011000", 0, 1, 0x20, 2), Symbol("caseD_0", 4, 1, 0, 3)],
    )
    report = relink([(0x11000, only)], {"caseD_0": 0x99999}, original, TEXT_VA)
    assert report.ok


def test_resolve_falls_back_to_the_name_without_its_namespace():
    table = {"D3DDevice_Clear": 0x243F00}
    assert resolve("D3D8::D3DDevice_Clear", table) == 0x243F00
    assert resolve("xboxkrnl.exe::NtClose", {}) is None


def test_an_import_resolves_to_its_thunk_in_text():
    table = {"thunk_XcSHAFinal": 0x10A2EC}
    assert resolve("xboxkrnl.exe::XcSHAFinal", table) == 0x10A2EC


def test_bytes_no_unit_writes_are_mismatches():
    # The missing bytes are zero in the original too, so only coverage catches them.
    original = b"\x90\xc3\x00\x00"
    only = unit(b"\x90\xc3", [], [Symbol("FUN_00011000", 0, 1, 0x20, 2)])
    report = relink([(0x11000, only)], {}, original, TEXT_VA)
    assert report.mismatches == [0x11002, 0x11003]


def test_overlapping_units_are_mismatches():
    original = b"\x90\x90\xc3"
    first = unit(b"\x90\x90", [], [Symbol("FUN_00011000", 0, 1, 0x20, 2)])
    second = unit(b"\x90\xc3", [], [Symbol("FUN_00011001", 0, 1, 0x20, 2)])
    report = relink([(0x11000, first), (0x11001, second)], {}, original, TEXT_VA)
    assert report.mismatches == [0x11001]


def test_unit_objects_must_match_the_units_list():
    expected = [Unit(0x11000, 0x11002), Unit(0x11002, 0x11004), Unit(0x11004, 0x11005)]
    objects = [
        (0x11000, unit(b"\x90\xc3", [], [Symbol("FUN_00011000", 0, 1, 0x20, 2)])),
        (0x11002, unit(b"\xc3", [], [Symbol("FUN_00011002", 0, 1, 0x20, 2)])),
        (0x11009, unit(b"\xc3", [], [Symbol("FUN_00011009", 0, 1, 0x20, 2)])),
    ]
    assert unit_problems(expected, objects) == [
        "0x00011002: object has 1 bytes, units list says 2",
        "0x00011004: no object",
        "0x00011009: object not in the units list",
    ]


def test_resolve_prefers_the_exact_literal_class_name():
    table = {"A::Update": 0x20000, "Update": 0x30000}
    assert resolve("A::Update", table) == 0x20000
