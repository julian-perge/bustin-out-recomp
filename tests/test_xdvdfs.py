import io

import pytest

from bodecomp.xdvdfs import extract, root_entries
from tests.isobuild import build_image

FILES = [
    ("media", b"m" * 10),
    ("default.xbe", b"XBEH" + b"x" * 3000),
    ("readme.txt", b"hi"),
    ("data.bin", b"d" * 5000),
]


def test_lists_every_root_entry():
    entries = root_entries(io.BytesIO(build_image(FILES)), partition=0)
    assert sorted(e.name for e in entries) == sorted(n for n, _ in FILES)


def test_extracts_file_on_left_branch_case_insensitively(tmp_path):
    iso = tmp_path / "disc.iso"
    iso.write_bytes(build_image(FILES))
    out = tmp_path / "out" / "default.xbe"
    assert extract(iso, "DEFAULT.XBE", out, partition=0) == 3004
    assert out.read_bytes() == b"XBEH" + b"x" * 3000


def test_extracts_file_spanning_sectors(tmp_path):
    iso = tmp_path / "disc.iso"
    iso.write_bytes(build_image(FILES))
    out = tmp_path / "data.bin"
    extract(iso, "data.bin", out, partition=0)
    assert out.read_bytes() == b"d" * 5000


def test_missing_file_raises(tmp_path):
    iso = tmp_path / "disc.iso"
    iso.write_bytes(build_image(FILES))
    with pytest.raises(FileNotFoundError, match="nope.xbe"):
        extract(iso, "nope.xbe", tmp_path / "x", partition=0)


def test_wrong_partition_offset_raises():
    with pytest.raises(ValueError, match="volume descriptor"):
        root_entries(io.BytesIO(build_image(FILES)), partition=2048)
