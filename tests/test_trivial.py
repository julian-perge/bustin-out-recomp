from pathlib import Path

import pytest

from bodecomp.cl import CompileResult, compile_cpp
from bodecomp.coff import Reloc, function_bytes, parse
from bodecomp.match import FLAGS, defined_function, read_functions, scan_source
from bodecomp.symbols import Entry, write_symbols
from bodecomp.trivial import (
    c_string,
    drop_conflicts,
    generate,
    masked,
    read_literals,
    recognise,
    shapes,
)
from bodecomp.xbe import Xbe
from tests.coffbuild import build_coff
from tests.test_match import ROOT, needs_toolchain
from tests.xbebuild import build_xbe

DIR32 = 0x6
ADDRESS = 0x00011000


def test_masked_drops_padding_and_masks_relocations():
    data = b"\xa1\x10\x20\x30\x00\xc3\xcc\xcc"
    assert masked(data, (Reloc(1, "DAT_00302010", DIR32),)) == "a1RRRRRRRRc3"


SHAPES = [
    ("empty", "c3", ()),
    ("empty-args", "c20800", ()),
    ("zero", "33c0c3", ()),
    ("false", "32c0c3", ()),
    ("true", "b001c3", ()),
    ("const", "b8feffffffc3", ()),
    ("this", "8bc1c3", ()),
    ("this-args", "8bc1c20400", ()),
    ("get", "8b01c3", ()),
    ("get", "8b4108c3", ()),
    ("get", "8b8184000000c3", ()),
    ("arg", "8b442404c3", ()),
    ("global", "a100000000c3", ((1, "DAT_00302010"),)),
    ("global16", "66a100000000c3", ((2, "DAT_00302010"),)),
    ("set-global", "8b442404a300000000c3", ((5, "DAT_00302010"),)),
    ("jump", "e900000000", ((1, "FUN_000136D0"),)),
    ("jump-pointer", "ff2500000000", ((2, "DAT_0035B7A4"),)),
    ("global-address", "b800000000c3", ((1, "DAT_002E2248"),)),
    ("set-second-arg", "8bc18b4c24088908c20800", ()),
    ("array-count", "8b0185c074048b40fcc333c0c3", ()),
    ("forward-member", "8b4c2404e900000000", ((5, "FUN_00049270"),)),
    ("delete-this", "85c974078b016a01ff5014c3", ()),
    ("vtable-destructor", "c70100000000c3", ((2, "PTR_FUN_002e21bc"),)),
    ("vtable-constructor", "8bc1c70000000000c3", ((4, "PTR_FUN_002e3cb8"),)),
]


def relocs(sites):
    return tuple(Reloc(o, name, DIR32) for o, name in sites)


@pytest.mark.parametrize(("shape", "hex_", "sites"), SHAPES)
def test_each_shape_is_recognised(shape, hex_, sites):
    g = recognise(ADDRESS, bytes.fromhex(hex_), relocs(sites), {})
    assert g is not None
    assert g.shape == shape
    assert g.code.startswith("// 0x00011000\n")


def test_member_at_offset_zero_has_no_padding():
    g = recognise(ADDRESS, bytes.fromhex("8b01c3"), (), {})
    assert not any("pad[" in d for d in g.decls)


def test_member_offset_sets_the_padding():
    g = recognise(ADDRESS, bytes.fromhex("8b8184000000c3"), (), {})
    assert any("char pad[0x84];" in d for d in g.decls)


def test_negative_displacement_is_not_recognised():
    assert recognise(ADDRESS, bytes.fromhex("8b41fcc3"), (), {}) is None


def test_const_with_a_relocation_returns_the_global_address():
    data = bytes.fromhex("b800000000c3")
    g = recognise(ADDRESS, data, relocs([(1, "DAT_00302010")]), {})
    assert g.decls == ("extern char DAT_00302010[];",)
    assert "return DAT_00302010;" in g.code


def test_const_with_a_relocation_to_a_known_string_returns_the_literal():
    data = bytes.fromhex("b800000000c3")
    literals = {0x002E2248: b"The Sims For PS2"}
    g = recognise(ADDRESS, data, relocs([(1, "DAT_002E2248")]), {}, literals)
    assert g.shape == "string-literal"
    assert g.decls == ()
    assert 'return "The Sims For PS2";' in g.code


def test_c_string_escapes_quotes_backslashes_trigraphs_and_high_bytes():
    assert c_string(b'a"b\\?\n\xe9') == '"a\\"b\\\\\\?\\012\\351"'


def test_jump_declares_its_callee():
    data = bytes.fromhex("e900000000")
    g = recognise(ADDRESS, data, relocs([(1, "FUN_000136D0")]), {})
    assert g.decls == ("void FUN_000136D0();",)
    assert "FUN_000136D0();" in g.code


def test_delete_this_puts_the_destructor_in_the_called_slot():
    g = recognise(ADDRESS, bytes.fromhex("85c974078b016a01ff5008c3"), (), {})
    (decl,) = g.decls
    assert "virtual void v1();" in decl and "virtual void v2();" not in decl
    assert "virtual ~S_00011000();" in decl
    assert "delete this;" in g.code


def test_vtable_stores_declare_a_virtual_destructor():
    dtor = recognise(ADDRESS, bytes.fromhex("c70100000000c3"), relocs([(2, "V")]), {})
    assert dtor.decls == ("struct S_00011000\n{\n    virtual ~S_00011000();\n};",)
    assert dtor.code.startswith("// 0x00011000\nS_00011000::~S_00011000()")
    data = bytes.fromhex("8bc1c70000000000c3")
    ctor = recognise(ADDRESS, data, relocs([(4, "V")]), {})
    assert "    virtual ~S_00011000() {}\n" in ctor.decls[0]
    assert ctor.code.startswith("// 0x00011000\nS_00011000::S_00011000()")


def test_delete_this_with_an_unaligned_slot_is_not_recognised():
    assert recognise(ADDRESS, bytes.fromhex("85c974078b016a01ff5006c3"), (), {}) is None


def test_a_caller_of_a_function_defined_in_its_block_is_dropped():
    callee = recognise(0x000136D0, bytes.fromhex("33c0c3"), (), {})
    caller = recognise(
        ADDRESS, bytes.fromhex("e900000000"), relocs([(1, "FUN_000136D0")]), {}
    )
    assert drop_conflicts([callee, caller]) == [callee]


def test_a_caller_of_a_vtable_store_in_its_block_is_kept():
    callee = recognise(
        0x000136D0, bytes.fromhex("c70100000000c3"), relocs([(2, "V")]), {}
    )
    caller = recognise(
        ADDRESS, bytes.fromhex("e900000000"), relocs([(1, "FUN_000136D0")]), {}
    )
    assert drop_conflicts([callee, caller]) == [callee, caller]


def test_two_declarations_of_one_global_keep_the_first():
    a = recognise(
        ADDRESS, bytes.fromhex("a100000000c3"), relocs([(1, "DAT_00302010")]), {}
    )
    b = recognise(
        0x11010, bytes.fromhex("b800000000c3"), relocs([(1, "DAT_00302010")]), {}
    )
    assert drop_conflicts([a, b]) == [a]


def test_const_is_signed():
    g = recognise(ADDRESS, bytes.fromhex("b8feffffffc3"), (), {})
    assert "return -2;" in g.code


def test_global_names_the_relocation_target():
    data = bytes.fromhex("a104000000c3")
    g = recognise(ADDRESS, data, relocs([(1, "DAT_00302010")]), {})
    assert g.decls == ("extern int DAT_00302014;",)


def test_global_named_in_the_target_table_gives_its_address():
    data = bytes.fromhex("a100000000c3")
    table = {"g_Counter": 0x00302010}
    g = recognise(ADDRESS, data, relocs([(1, "g_Counter")]), table)
    assert g.decls == ("extern int DAT_00302010;",)


def test_empty_args_counts_its_arguments():
    g = recognise(ADDRESS, bytes.fromhex("c20800"), (), {})
    assert "FUN_00011000(int a1, int a2)" in g.code


def test_unknown_pattern_is_none():
    assert recognise(ADDRESS, bytes.fromhex("40c3"), (), {}) is None


EXTERNAL = 2
FUNCTION = 0x20
UNITS = {0x11000: "c3", 0x11010: "33c0c3"}


def obj(bodies: dict[str, str]) -> bytes:
    data, symbols = b"", []
    for name, hex_ in bodies.items():
        symbols.append((name, len(data), 1, FUNCTION, EXTERNAL))
        data += bytes.fromhex(hex_)
    return build_coff(sections=[(".text", data, [])], symbols=symbols)


BUILT = obj({"?FUN_00011000@@YAXXZ": "c3", "?FUN_00011010@@YAHXZ": "32c0c3"})


def fake_compile(built: bytes, fail_under: str | None = None):
    def stub(root, source, output, flags):
        if fail_under and source.is_relative_to(fail_under):
            return CompileResult(False, output, "x.cpp(1) : error C2143: syntax")
        (root / output).parent.mkdir(parents=True, exist_ok=True)
        (root / output).write_bytes(built)
        return CompileResult(True, output, "")

    return stub


def repo(tmp_path: Path, units=UNITS) -> Path:
    (tmp_path / "src/game").mkdir(parents=True)
    (tmp_path / "orig").mkdir()
    (tmp_path / "orig/default.xbe").write_bytes(
        build_xbe([(".text", 0x11000, b"\xcc" * 0x40)], [], title_id=1, entry=0x11000)
    )
    unit_dir = tmp_path / "build/target/units"
    unit_dir.mkdir(parents=True)
    for address, hex_ in units.items():
        (unit_dir / f"{address:08X}.obj").write_bytes(
            build_coff([(".text", bytes.fromhex(hex_) + b"\xcc", [])], [])
        )
    (tmp_path / "build/target/units.txt").write_text(
        "".join(f"{a:08X} {a + 0x10:08X}\n" for a in units)
    )
    (tmp_path / "build/target/symbols.tsv").write_text("")
    (tmp_path / "build/strings.tsv").write_text("")
    (tmp_path / "config").mkdir()
    write_symbols(
        tmp_path / "config/symbols.txt",
        [Entry(a, "function", 16, f"FUN_{a:08X}", "auto", "") for a in units],
    )
    return tmp_path


def tree(root: Path) -> dict[str, str]:
    files = sorted((root / "src/game/trivial").glob("*.cpp"))
    files.append(root / "config/functions.csv")
    return {p.relative_to(root).as_posix(): p.read_text() for p in files}


def test_generate_keeps_matched_and_drops_nonmatching(tmp_path):
    root = repo(tmp_path)
    kept, tried, problems = generate(root, compile=fake_compile(BUILT))
    assert problems == []
    assert (kept, tried) == ({"empty": 1, "zero": 0}, {"empty": 1, "zero": 1})
    text = (root / "src/game/trivial/0001.cpp").read_text()
    assert "FUN_00011000" in text and "FUN_00011010" not in text
    assert read_functions(root / "config/functions.csv") == {
        0x11000: ("matched", "src/game/trivial/0001.cpp")
    }


def test_generate_is_idempotent(tmp_path):
    root = repo(tmp_path)
    generate(root, compile=fake_compile(BUILT))
    first = tree(root)
    generate(root, compile=fake_compile(BUILT))
    assert tree(root) == first


def test_generate_skips_functions_claimed_by_other_sources(tmp_path):
    root = repo(tmp_path)
    (root / "src/game/a.cpp").write_text("// 0x00011000\nvoid FUN_00011000()\n{\n}\n")
    kept, tried, problems = generate(root, compile=fake_compile(BUILT))
    assert problems == []
    assert tried == {"zero": 1}
    assert not (root / "src/game/trivial/0001.cpp").exists()


def test_generate_drops_a_trivial_function_claimed_by_another_source(tmp_path):
    root = repo(tmp_path)
    generate(root, compile=fake_compile(BUILT))
    (root / "src/game/a.cpp").write_text("// 0x00011000\nvoid FUN_00011000()\n{\n}\n")
    kept, tried, problems = generate(root, compile=fake_compile(BUILT))
    assert problems == []
    assert tried == {"zero": 1}
    assert not (root / "src/game/trivial/0001.cpp").exists()


def test_generate_leaves_trivial_untouched_when_a_block_fails_to_compile(tmp_path):
    root = repo(tmp_path)
    generate(root, compile=fake_compile(BUILT))
    before = tree(root)
    _, _, problems = generate(root, compile=fake_compile(BUILT, "build/trivial"))
    assert problems == ["0001: x.cpp(1) : error C2143: syntax"]
    assert tree(root) == before


def test_generate_needs_the_string_export(tmp_path):
    root = repo(tmp_path)
    (root / "build/strings.tsv").unlink()
    _, _, problems = generate(root, compile=fake_compile(BUILT))
    assert problems == ["build/strings.tsv is missing; run tools/export-strings.sh"]


def test_read_literals_keeps_strings_whose_text_matches_the_xbe(tmp_path):
    xbe = Xbe.parse(
        build_xbe(
            [(".rdata", 0x2000, b"Hi\x00\xe9t\xe9\x00Old\x00")],
            [],
            title_id=1,
            entry=0x2000,
        )
    )
    tsv = tmp_path / "strings.tsv"
    tsv.write_text(
        "00011000\t00002000\tHi\n"
        "00011010\t00002003\t\\u00e9t\\u00e9\n"
        "00011020\t00002007\tNew\n"
    )
    assert read_literals(tsv, xbe) == {0x2000: b"Hi", 0x2003: b"\xe9t\xe9"}


def test_shapes_counts_patterns_and_names_the_claiming_shape(tmp_path):
    units = {0x11000: "c3", 0x11010: "c3", 0x11020: "33c0c3", 0x11030: "e9"}
    root = repo(tmp_path, units)
    assert shapes(root, 2) == [("c3", 2, "empty"), ("33c0c3", 1, "zero")]
    assert shapes(root, 5)[-1] == ("e9", 1, "-")


@needs_toolchain
@pytest.mark.parametrize(("shape", "hex_", "sites"), SHAPES)
def test_every_shape_compiles_to_its_pattern(shape, hex_, sites):
    data, target_relocs = bytes.fromhex(hex_), relocs(sites)
    g = recognise(ADDRESS, data, target_relocs, {})
    source = Path(f"build/test-trivial/{shape}-{len(data)}.cpp")
    (ROOT / source).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / source).write_text("\n".join(g.decls) + "\n\n" + g.code)
    result = compile_cpp(ROOT, source, source.with_suffix(".obj"), FLAGS)
    assert result.ok, result.log
    coff = parse((ROOT / result.output).read_bytes())
    (marked,), _ = scan_source(source, g.code)
    built, built_relocs = function_bytes(coff, defined_function(coff, marked.name))
    assert masked(built, built_relocs) == masked(data, target_relocs)
