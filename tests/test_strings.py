from bodecomp.strings import StringRef, read_refs, unescape


def test_unescape_reverses_the_java_escapes():
    assert unescape("a\\tb\\\\n\\u00e9\\r\\n") == "a\tb\\n\u00e9\r\n"


def test_unescape_leaves_plain_text_alone():
    assert unescape("Sun Color Last") == "Sun Color Last"


def test_read_refs_groups_by_function_in_file_order(tmp_path):
    path = tmp_path / "strings.tsv"
    path.write_text(
        "000133F0\t002E5000\tAllocating CTGDump object memory\\n\n"
        "000133F0\t002E5040\trletextures\n"
        "00033E30\t002E6000\tsystem.cnf\n"
    )
    assert read_refs(path) == {
        0x133F0: [
            StringRef(0x2E5000, "Allocating CTGDump object memory\n"),
            StringRef(0x2E5040, "rletextures"),
        ],
        0x33E30: [StringRef(0x2E6000, "system.cnf")],
    }
