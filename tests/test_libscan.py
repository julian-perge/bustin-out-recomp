from bodecomp.libscan import files_containing


def test_reports_only_files_containing_the_bytes(tmp_path):
    a = tmp_path / "a.lib"
    b = tmp_path / "b.lib"
    a.write_bytes(b"xx\x8b\x41\x08\xc3yy")
    b.write_bytes(b"\x8b\x41\x0c\xc3")
    assert files_containing(b"\x8b\x41\x08\xc3", [a, b]) == [a]
