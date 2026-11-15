import hashlib

import pytest

from bodecomp.setup_inputs import install_xbe
from tests.isobuild import build_image

XBE = b"XBEH" + b"z" * 100


def make_iso(tmp_path):
    iso = tmp_path / "disc.iso"
    iso.write_bytes(build_image([("default.xbe", XBE)]))
    return iso


def test_installs_when_hash_matches(tmp_path):
    expected = hashlib.sha256(XBE).hexdigest()
    dest = tmp_path / "orig" / "default.xbe"
    digest = install_xbe(make_iso(tmp_path), dest, expected=expected, partition=0)
    assert digest == expected
    assert dest.read_bytes() == XBE


def test_wrong_hash_names_both_and_leaves_nothing(tmp_path):
    dest = tmp_path / "orig" / "default.xbe"
    with pytest.raises(ValueError) as info:
        install_xbe(make_iso(tmp_path), dest, expected="ab" * 32, partition=0)
    message = str(info.value)
    assert hashlib.sha256(XBE).hexdigest() in message
    assert "ab" * 32 in message
    assert not dest.exists()
    assert list(dest.parent.iterdir()) == []
