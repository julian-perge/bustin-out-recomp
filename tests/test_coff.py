import struct

import pytest

from bodecomp.coff import find_symbol, function_bytes, parse
from tests.coffbuild import build_coff

FUNC = 0x20
EXTERNAL = 2
STATIC = 3
WEAK_EXTERNAL = 105

GETTER = b"\x8b\x41\x08\xc3"
ADDER = b"\x8b\x44\x24\x04\x03\x44\x24\x08\xc3"


def comdat_layout() -> bytes:
    return build_coff(
        sections=[(".text", GETTER, []), (".text", ADDER, [])],
        symbols=[
            (".text", 0, 1, 0, STATIC),
            ("?getCount@Room@@QAEHXZ", 0, 1, FUNC, EXTERNAL),
            (".text", 0, 2, 0, STATIC),
            ("?fn_00012340@@YAHHH@Z", 0, 2, FUNC, EXTERNAL),
        ],
    )


def shared_section_layout() -> bytes:
    return build_coff(
        sections=[(".text", GETTER + ADDER, [(5, 3, 6)])],
        symbols=[
            (".text", 0, 1, 0, STATIC),
            ("_getter", 0, 1, FUNC, EXTERNAL),
            ("_adder", len(GETTER), 1, FUNC, EXTERNAL),
            ("_g_value", 0, 0, 0, EXTERNAL),
        ],
    )


def test_finds_decorated_cpp_name_by_plain_name():
    coff = parse(comdat_layout())
    assert find_symbol(coff, "fn_00012340").name == "?fn_00012340@@YAHHH@Z"


def test_finds_c_name_with_underscore():
    assert find_symbol(parse(shared_section_layout()), "adder").name == "_adder"


def test_unknown_name_lists_defined_symbols():
    with pytest.raises(LookupError, match="getCount"):
        find_symbol(parse(comdat_layout()), "missing")


def test_comdat_function_gets_its_own_section_bytes():
    coff = parse(comdat_layout())
    code, relocs = function_bytes(coff, find_symbol(coff, "fn_00012340"))
    assert code == ADDER
    assert relocs == ()


def test_shared_section_splits_at_next_symbol_and_rebases_relocs():
    coff = parse(shared_section_layout())
    getter, getter_relocs = function_bytes(coff, find_symbol(coff, "getter"))
    adder, adder_relocs = function_bytes(coff, find_symbol(coff, "adder"))
    assert getter == GETTER
    assert getter_relocs == ()
    assert adder == ADDER
    assert [(r.offset, r.symbol, r.type) for r in adder_relocs] == [(1, "_g_value", 6)]


def test_long_symbol_names_come_from_string_table():
    coff = parse(comdat_layout())
    assert "?getCount@Room@@QAEHXZ" in [s.name for s in coff.symbols]


def test_labels_inside_a_function_do_not_end_it():
    label_class = 6
    coff = parse(
        build_coff(
            sections=[(".text", GETTER + ADDER, [])],
            symbols=[
                (".text", 0, 1, 0, STATIC),
                ("_getter", 0, 1, FUNC, EXTERNAL),
                ("$L1234", 2, 1, 0, label_class),
                ("_adder", len(GETTER), 1, FUNC, EXTERNAL),
            ],
        )
    )
    code, _ = function_bytes(coff, find_symbol(coff, "getter"))
    assert code == GETTER


def test_weak_external_names_the_symbol_it_stands_for():
    tag = struct.pack("<II", 0, 2).ljust(18, b"\0")
    obj = build_coff(
        sections=[(".text", b"\xc3", [])],
        symbols=[
            ("??_GFoo@@UAEPAXI@Z", 0, 0, FUNC, EXTERNAL),
            ("??_EFoo@@UAEPAXI@Z", 0, 0, FUNC, WEAK_EXTERNAL, tag),
        ],
    )
    weak = parse(obj).symbols[1]
    assert weak.alias == "??_GFoo@@UAEPAXI@Z"
    assert parse(obj).symbols[0].alias is None
