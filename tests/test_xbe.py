import pytest

from bodecomp.xbe import Library, Xbe
from tests.xbebuild import build_xbe


def sample() -> Xbe:
    data = build_xbe(
        sections=[(".text", 0x11000, b"\x55\x8b\xec\xc3"), (".data", 0x20000, b"ab")],
        libraries=[("XAPILIB", 5558), ("D3D8", 5558)],
        title_id=0x45410043,
        entry=0x11000,
    )
    return Xbe.parse(data)


def test_parses_header_fields():
    xbe = sample()
    assert xbe.base == 0x10000
    assert xbe.entry == 0x11000
    assert xbe.title_id == 0x45410043


def test_parses_sections_and_libraries():
    xbe = sample()
    assert [s.name for s in xbe.sections] == [".text", ".data"]
    assert xbe.sections[0].va == 0x11000
    assert xbe.libraries == (
        Library("XAPILIB", 1, 0, 5558),
        Library("D3D8", 1, 0, 5558),
    )


def test_read_returns_section_bytes():
    assert sample().read(0x11001, 2) == b"\x8b\xec"


def test_read_rejects_range_past_section_end():
    with pytest.raises(ValueError, match="0x00011003"):
        sample().read(0x11003, 2)


def test_rejects_non_xbe():
    with pytest.raises(ValueError, match="XBEH"):
        Xbe.parse(b"MZ" + bytes(0x200))
