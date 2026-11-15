import pytest

from bodecomp.coff import CoffSection, Reloc, Symbol
from bodecomp.unitsplit import (
    DelinkReloc,
    NamedAddress,
    build_unit,
    read_relocs,
    read_symbol_table,
)

CODE = 0x60000020
COMMENT = CoffSection(".comment", b"ghidra-delinker-extension x\0", (), 0xA00)
TEXT_VA = 0x11000
# Two units: 0x11000-0x11010 calls 0x11010 and reads 0x2E2248; 0x11010-0x11020
# jumps inside itself.
TEXT = bytes(range(0x20))
NAMES = {
    0x11000: NamedAddress("FUN_00011000", function=True, static=False),
    0x11008: NamedAddress("LAB_00011008", function=False, static=True),
    0x11010: NamedAddress("FUN_00011010", function=True, static=False),
    0x11018: NamedAddress("LAB_00011018", function=False, static=True),
    0x2E2248: NamedAddress("s_The_Sims_002e2248", function=False, static=False),
}


def unit(start, end, relocs):
    return build_unit(start, end, TEXT, TEXT_VA, relocs, NAMES, COMMENT)


def test_a_call_out_of_the_unit_becomes_a_rel32_to_an_undefined_symbol():
    call = DelinkReloc(0x11001, "R", 4, 0x11010, -4, (0x11010,))
    sections, symbols = unit(0x11000, 0x11010, [call])
    text = sections[0]
    assert text.relocs == (Reloc(1, "FUN_00011010", 0x14),)
    assert text.data[1:5] == (0).to_bytes(4, "little")
    assert Symbol("FUN_00011010", 0, 0, 0x20, 2) in symbols


def test_an_absolute_reference_is_patched_with_its_addend():
    read = DelinkReloc(0x11006, "A", 4, 0x2E2248, 2, None)
    sections, symbols = unit(0x11000, 0x11010, [read])
    assert sections[0].relocs == (Reloc(6, "s_The_Sims_002e2248", 6),)
    assert sections[0].data[6:10] == (2).to_bytes(4, "little")
    assert sections[0].data[:6] == TEXT[:6]
    assert sections[0].data[10:] == TEXT[10:0x10]


def test_a_jump_that_stays_in_the_unit_keeps_its_bytes_and_has_no_relocation():
    jump = DelinkReloc(0x11012, "R", 4, 0x11018, -4, (0x11018,))
    sections, _ = unit(0x11010, 0x11020, [jump])
    assert sections[0].relocs == ()
    assert sections[0].data == TEXT[0x10:0x20]


def test_an_opaque_relative_reference_inside_the_unit_keeps_its_relocation():
    jump = DelinkReloc(0x11012, "R", 4, 0x11018, -4, None)
    sections, _ = unit(0x11010, 0x11020, [jump])
    assert sections[0].relocs == (Reloc(2, "LAB_00011018", 0x14),)


def test_symbols_follow_the_exporter_order():
    relocs = [
        DelinkReloc(0x11001, "R", 4, 0x11010, -4, (0x11010,)),
        DelinkReloc(0x11006, "A", 4, 0x2E2248, 0, None),
    ]
    _, symbols = unit(0x11000, 0x11010, relocs)
    assert symbols == [
        Symbol(".file", 0, -2, 0, 103),
        Symbol(".text", 0, 1, 0, 3),
        Symbol("FUN_00011000", 0, 1, 0x20, 2),
        Symbol("LAB_00011008", 8, 1, 0, 3),
        Symbol("FUN_00011010", 0, 0, 0x20, 2),
        Symbol("s_The_Sims_002e2248", 0, 0, 0x20, 2),
    ]


def test_the_comment_section_follows_the_text():
    sections, _ = unit(0x11000, 0x11010, [])
    assert [s.name for s in sections] == [".text", ".comment"]
    assert sections[0].characteristics == CODE
    assert sections[1] == COMMENT


def test_a_relocation_to_an_address_without_a_name_is_an_error():
    stray = DelinkReloc(0x11006, "A", 4, 0x2E9999, 0, None)
    with pytest.raises(KeyError, match="0x002E9999"):
        unit(0x11000, 0x11010, [stray])


def test_read_relocs_parses_the_ghidra_table(tmp_path):
    path = tmp_path / "relocs.tsv"
    path.write_text(
        "00011021\tR\t4\tFFFFFFFF\t000136D0\t-4\tT:000136D0,00011030\n"
        "00011041\tA\t4\tFFFFFFFF\t003DCE94\t0\t-\n"
        "00011051\tR\t4\tFFFFFFFF\t000136E0\t-4\tT:\n"
    )
    assert read_relocs(path) == [
        DelinkReloc(0x11021, "R", 4, 0x136D0, -4, (0x136D0, 0x11030)),
        DelinkReloc(0x11041, "A", 4, 0x3DCE94, 0, None),
        DelinkReloc(0x11051, "R", 4, 0x136E0, -4, ()),
    ]


def test_read_symbol_table_parses_the_ghidra_table(tmp_path):
    path = tmp_path / "symbols.tsv"
    path.write_text("00000004\t0\t0\tXAPILIB::_tls_array\n00011000\t1\t0\tentry\n")
    assert read_symbol_table(path) == {
        0x4: NamedAddress("XAPILIB::_tls_array", function=False, static=False),
        0x11000: NamedAddress("entry", function=True, static=False),
    }


def test_a_short_jump_out_of_the_unit_is_left_unpatched_but_names_its_target():
    jump = DelinkReloc(0x1100E, "R", 1, 0x11018, -1, (0x11018,))
    sections, symbols = unit(0x11000, 0x11010, [jump])
    assert sections[0].relocs == ()
    assert sections[0].data == TEXT[:0x10]
    assert Symbol("LAB_00011018", 0, 0, 0x20, 2) in symbols


def test_a_dropped_relocation_to_an_address_without_a_name_adds_no_external():
    jump = DelinkReloc(0x1100E, "R", 1, 0x2E9999, -1, (0x2E9999,))
    _, symbols = unit(0x11000, 0x11010, [jump])
    assert [s.name for s in symbols if s.section == 0] == []


def test_read_relocs_parses_a_one_byte_relocation(tmp_path):
    path = tmp_path / "relocs.tsv"
    path.write_text("000110BB\tR\t1\tFF\t000110DF\t-1\tT:000110DF\n")
    assert read_relocs(path) == [DelinkReloc(0x110BB, "R", 1, 0x110DF, -1, (0x110DF,))]
