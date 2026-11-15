import pytest

from bodecomp.coff import CoffSection, Reloc, Symbol, parse
from bodecomp.coffwrite import write_coff

CODE = 0x60000020


def test_round_trip_with_undefined_and_long_names():
    sections = [
        CoffSection(
            ".text",
            b"\xe8\x00\x00\x00\x00\xa1\x00\x00\x00\x00\xc3",
            (
                Reloc(1, "?LongFunctionName@Class@@QAEXXZ", 0x14),
                Reloc(6, "DAT_002e21a8", 6),
            ),
            CODE,
        )
    ]
    symbols = [
        Symbol("FUN_00011000", 0, 1, 0x20, 2),
        Symbol("?LongFunctionName@Class@@QAEXXZ", 0, 0, 0x20, 2),
        Symbol("DAT_002e21a8", 0, 0, 0, 2),
    ]
    parsed = parse(write_coff(sections, symbols))
    assert parsed.sections == tuple(sections)
    assert parsed.symbols == tuple(symbols)


def test_unknown_relocation_symbol_is_an_error():
    sections = [CoffSection(".text", b"\x00" * 4, (Reloc(0, "missing", 6),), CODE)]
    with pytest.raises(KeyError, match="missing"):
        write_coff(sections, [])
