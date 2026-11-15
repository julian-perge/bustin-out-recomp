from pathlib import Path

import pytest

from bodecomp.cl import CL, WIBO, CompileResult, compile_cpp
from bodecomp.coff import Reloc, parse
from bodecomp.match import (
    Resolver,
    candidates,
    compare,
    decorated_prefixes,
    defined_function,
    main,
    read_functions,
    run,
    scan_source,
    scope_path,
)
from bodecomp.symbols import Entry, write_symbols
from bodecomp.xbe import Xbe
from tests.coffbuild import build_coff
from tests.xbebuild import build_xbe

ROOT = Path(__file__).resolve().parents[1]
DATA = 0xC0000040
DIR32, REL32 = 0x6, 0x14
EXTERNAL, STATIC, WEAK_EXTERNAL = 2, 3, 105


def xbe_with(rdata: bytes = b"hi\0\0", text: bytes = b"\xcc" * 0x20) -> Xbe:
    return Xbe.parse(
        build_xbe(
            [(".text", 0x11000, text), (".rdata", 0x20000, rdata)],
            [],
            title_id=1,
            entry=0x11000,
        )
    )


def resolver(
    obj: bytes, addresses=None, entries=(), rdata=b"hi\0\0", text=b"\xcc" * 0x20
) -> Resolver:
    return Resolver(parse(obj), addresses or {}, list(entries), xbe_with(rdata, text))


def entry(address: int, name: str) -> Entry:
    return Entry(address, "data", 0, name, "string", "string:0x00020000")


PUSH = b"\x68\0\0\0\0\xc3"


def push_obj(symbols, sections=()) -> bytes:
    return build_coff(
        sections=[(".text", PUSH, [(1, 1, DIR32)]), *sections],
        symbols=[("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL), *symbols],
    )


def check(obj, unit=PUSH, unit_relocs=None, **kw):
    coff = parse(obj)
    built = coff.sections[0]
    relocs = tuple(r for r in built.relocs if r.offset < len(PUSH))
    if unit_relocs is None:
        unit_relocs = (Reloc(1, "DAT_00020000", DIR32),)
    return compare(
        0x11000, unit, unit_relocs, built.data, relocs, resolver(obj, **kw), {}
    )


def test_string_literal_matches_the_original_bytes():
    obj = push_obj([("$SG1", 0, 2, 0, STATIC)], [(".data", b"hi\0\0", [], DATA)])
    assert check(obj) == ("matched", "100.0", "")


def test_string_literal_with_other_text_does_not_match():
    obj = push_obj([("$SG1", 0, 2, 0, STATIC)], [(".data", b"ho\0\0", [], DATA)])
    status, score, detail = check(obj)
    assert status == "nonmatching"
    assert "relocation at +0x1" in detail and "differs" in detail
    assert score == "33.3"


def test_external_resolves_through_its_scope_path():
    obj = push_obj([("?g_x@Foo@@2HA", 0, 0, 0, EXTERNAL)])
    assert check(obj, entries=[entry(0x20000, "Foo::g_x")])[0] == "matched"


def test_external_named_twice_in_symbols_does_not_resolve():
    obj = push_obj([("?g_x@Foo@@2HA", 0, 0, 0, EXTERNAL)])
    twice = [entry(0x20000, "Foo::g_x"), entry(0x20004, "Foo::g_x")]
    status, _, detail = check(obj, entries=twice)
    assert status == "nonmatching"
    assert "names 2 entries" in detail


def test_auto_name_gives_its_address():
    obj = push_obj([("_DAT_00020000", 0, 0, 0, EXTERNAL)])
    assert check(obj)[0] == "matched"
    wrong = push_obj([("_DAT_00020004", 0, 0, 0, EXTERNAL)])
    assert "built 0x00020004" in check(wrong)[2]


def test_target_relocation_missing_from_the_build():
    obj = build_coff(
        sections=[(".text", PUSH, [])],
        symbols=[("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL)],
    )
    status, _, detail = check(obj)
    assert status == "nonmatching"
    assert "built has none" in detail


CALL = b"\xe8\0\0\0\0\xc3"


def call_obj() -> bytes:
    return build_coff(
        sections=[(".text", CALL + b"\xc3", [(1, 1, REL32)])],
        symbols=[
            ("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL),
            ("?g@@YAXXZ", 6, 1, 0x20, EXTERNAL),
        ],
    )


def call_check(unit, unit_relocs):
    obj = call_obj()
    coff = parse(obj)
    built = coff.sections[0]
    addresses = {"?f@@YAXXZ": 0x11000, "?g@@YAXXZ": 0x11010}
    return compare(
        0x11000,
        unit,
        unit_relocs,
        built.data[:6],
        built.relocs,
        resolver(obj, addresses),
        {},
    )


def test_call_to_a_local_function_resolves_through_its_address_comment():
    unit_relocs = (Reloc(1, "FUN_00011010", REL32),)
    assert call_check(CALL, unit_relocs)[0] == "matched"


def test_call_the_delinker_dropped_compares_with_the_literal_offset():
    literal = b"\xe8" + (0x11010 - 0x11005).to_bytes(4, "little") + b"\xc3"
    assert call_check(literal, ())[0] == "matched"
    wrong = b"\xe8" + (0x11020 - 0x11005).to_bytes(4, "little") + b"\xc3"
    assert "target 0x00011020" in call_check(wrong, ())[2]


def bare(unit: bytes, built: bytes):
    obj = build_coff(sections=[(".text", built, [])], symbols=[])
    return compare(0x11000, unit, (), built, (), resolver(obj), {})


def test_trailing_padding_in_the_unit_is_allowed():
    assert bare(b"\x8b\x41\x08\xc3\xcc\x90", b"\x8b\x41\x08\xc3")[0] == "matched"


def test_trailing_code_in_the_unit_is_a_difference():
    status, score, detail = bare(b"\x8b\x41\x08\xc3\x90\xc3", b"\x8b\x41\x08\xc3")
    assert status == "nonmatching"
    assert "first difference at +0x4" in detail
    assert score == "66.7"


def test_a_build_longer_than_the_unit_is_a_difference():
    assert bare(b"\x8b\x41\x08\xc3", b"\x8b\x41\x08\x90\xc3")[0] == "nonmatching"


def test_scan_reads_address_parked_class_and_name():
    text = (
        "// 0x00011000\n"
        "int Foo::Bar(int a,\n"
        "             int b)\n"
        "{\n}\n"
        "// 0x00011010\n"
        "// parked: register tie\n"
        "Foo::~Foo()\n{\n}\n"
        "// 0x00011020\n"
        "// parked: bad luck\n"
        "bool operator==(A a, A b)\n{\n}\n"
    )
    found, problems = scan_source(Path("src/a.cpp"), text)
    assert [(m.address, m.name, m.parked) for m in found] == [
        (0x11000, "Foo::Bar", ""),
        (0x11010, "Foo::~Foo", "register tie"),
    ]
    assert problems == [
        "src/a.cpp:12: unknown blocker class 'bad luck'",
        "src/a.cpp:11: no function definition follows",
    ]


def test_decorated_prefixes():
    assert decorated_prefixes("A::B::f") == ("?f@B@A@@",)
    assert decorated_prefixes("A::A") == ("??0A@@",)
    assert decorated_prefixes("N::A::~A") == ("??1A@N@@",)
    assert decorated_prefixes("f") == ("?f@@", "_f")
    assert decorated_prefixes("operator delete") == ("??3@",)
    assert decorated_prefixes("A::operator new") == ("??2A@@",)


def test_scan_reads_operator_new_and_delete():
    text = (
        "// 0x00011000\n"
        "void operator delete(void* p)\n{\n}\n"
        "// 0x00011010\n"
        "void* Foo::operator new(unsigned n)\n{\n}\n"
    )
    found, problems = scan_source(Path("src/a.cpp"), text)
    assert [m.name for m in found] == ["operator delete", "Foo::operator new"]
    assert problems == []


def test_scope_path():
    assert scope_path("?g_x@Foo@@2HA") == "Foo::g_x"
    assert scope_path("?Run@Inner@Outer@@QAEXXZ") == "Outer::Inner::Run"
    assert scope_path("_FUN_000136d0") == "FUN_000136d0"
    assert scope_path("??0Foo@@QAE@XZ") is None
    assert scope_path("__ftol2") is None


def fake_compile(obj: bytes):
    def stub(root, source, output, flags):
        (root / output).parent.mkdir(parents=True, exist_ok=True)
        (root / output).write_bytes(obj)
        return CompileResult(True, output, "")

    return stub


def project(tmp_path: Path, source: str) -> Path:
    (tmp_path / "src/game").mkdir(parents=True)
    (tmp_path / "src/game/a.cpp").write_text(source)
    (tmp_path / "src/m0").mkdir()
    (tmp_path / "src/m0/fn.cpp").write_text("// 0x00011000\nvoid fn() {}\n")
    (tmp_path / "orig").mkdir()
    (tmp_path / "orig/default.xbe").write_bytes(
        build_xbe([(".text", 0x11000, CALL)], [], title_id=1, entry=0x11000)
    )
    units = tmp_path / "build/target/units"
    units.mkdir(parents=True)
    (units / "00011000.obj").write_bytes(
        build_coff(
            sections=[(".text", CALL, [(1, 0, REL32)])],
            symbols=[("FUN_00011010", 0, 0, 0x20, EXTERNAL)],
        )
    )
    (tmp_path / "build/target/symbols.tsv").write_text("00011010\t1\t0\tFUN_00011010\n")
    (tmp_path / "config").mkdir()
    write_symbols(tmp_path / "config/symbols.txt", [])
    return tmp_path


def test_run_skips_m0_and_marks_parked(tmp_path, monkeypatch):
    source = "// 0x00011000\n// parked: scheduling\nvoid f()\n{\n}\n"
    root = project(tmp_path, source)
    obj = build_coff(
        sections=[(".text", CALL, [(1, 1, REL32)])],
        symbols=[
            ("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL),
            ("_FUN_00011010", 0, 0, 0x20, EXTERNAL),
        ],
    )
    results, problems = run(root, compile=fake_compile(obj))
    assert problems == []
    assert [(r.address, r.status, r.score, r.detail) for r in results] == [
        (0x11000, "parked", "100.0", "scheduling")
    ]


def test_check_fails_on_a_stale_csv(tmp_path, monkeypatch):
    root = project(tmp_path, "// 0x00011000\nvoid f()\n{\n}\n")
    obj = build_coff(
        sections=[(".text", CALL, [(1, 1, REL32)])],
        symbols=[
            ("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL),
            ("_FUN_00011010", 0, 0, 0x20, EXTERNAL),
        ],
    )
    monkeypatch.chdir(root)
    monkeypatch.setattr("bodecomp.match.compile_cpp", fake_compile(obj))
    assert main(["--check"]) == 1
    assert main([]) == 0
    assert read_functions(root / "config/functions.csv") == {
        0x11000: ("matched", "src/game/a.cpp")
    }
    assert main(["--check"]) == 0


def test_two_sources_claiming_one_address_is_a_problem(tmp_path):
    root = project(tmp_path, "// 0x00011010\nvoid f()\n{\n}\n")
    (root / "src/game/b.cpp").write_text("// 0x00011010\nvoid g()\n{\n}\n")
    _, problems = run(root, compile=fake_compile(b""))
    assert problems == ["0x00011010 is claimed by src/game/a.cpp and src/game/b.cpp"]


needs_toolchain = pytest.mark.skipif(
    not (ROOT / WIBO).exists() or not (ROOT / CL).exists(),
    reason="VC71 toolchain is not set up",
)


@needs_toolchain
def test_definitions_are_found_among_vc71_decorated_names():
    source = Path("build/test-match/names.cpp")
    (ROOT / source).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / source).write_text(
        "struct Foo { Foo(); ~Foo(); int Get(); int m; };\n"
        "Foo::Foo() { m = 1; }\n"
        "Foo::~Foo() { m = 0; }\n"
        "int Foo::Get() { return m; }\n"
        "int Free() { return 2; }\n"
        'extern "C" int Plain() { return 3; }\n'
    )
    result = compile_cpp(ROOT, source, source.with_suffix(".obj"), ("/O2",))
    assert result.ok, result.log
    coff = parse((ROOT / result.output).read_bytes())
    names = ["Foo::Foo", "Foo::~Foo", "Foo::Get", "Free", "Plain"]
    assert [defined_function(coff, n).name for n in names] == [
        "??0Foo@@QAE@XZ",
        "??1Foo@@QAE@XZ",
        "?Get@Foo@@QAEHXZ",
        "?Free@@YAHXZ",
        "_Plain",
    ]


def test_relocation_of_another_type_does_not_match():
    obj = build_coff(
        sections=[(".text", PUSH, [(1, 1, REL32)])],
        symbols=[
            ("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL),
            ("_DAT_00020000", 0, 0, 0, EXTERNAL),
        ],
    )
    status, _, detail = check(obj)
    assert status == "nonmatching"
    assert "type 0x14, target 0x6" in detail


def vtable_check(slot: str):
    # The original vtable at 0x20000 holds one pointer, to 0x00011010.
    rdata = (0x11010).to_bytes(4, "little")
    obj = push_obj(
        [("??_7Foo@@6B@", 0, 2, 0, STATIC), (slot, 0, 0, 0x20, EXTERNAL)],
        [(".rdata", b"\0\0\0\0", [(0, 2, DIR32)], 0x40000040)],
    )
    return check(obj, rdata=rdata)


def test_vtable_slots_are_checked_against_the_original_pointers():
    assert vtable_check("_FUN_00011010")[0] == "matched"
    status, _, detail = vtable_check("_FUN_00011020")
    assert status == "nonmatching"
    assert "points elsewhere" in detail


def test_candidates_skip_listed_sdk_and_small_units_and_sort_by_relocations(tmp_path):
    units = tmp_path / "build/target/units"
    units.mkdir(parents=True)
    bodies = {
        0x11000: (b"\x40" * 19 + b"\xc3" + b"\xcc" * 12, []),
        0x11020: (b"\x40" * 7 + b"\xc3" + b"\x90" * 8, []),
        0x11030: (b"\xe8\0\0\0\0" + b"\x40" * 14 + b"\xc3", [(1, 0, REL32)]),
        0x11050: (b"\x40" * 17 + b"\xc3", []),
        0x11070: (b"\x40" * 16 + b"\xc3", []),
    }
    for address, (body, relocs) in bodies.items():
        (units / f"{address:08X}.obj").write_bytes(
            build_coff(
                sections=[(".text", body, relocs)],
                symbols=[("FUN_00011010", 0, 0, 0x20, EXTERNAL)],
            )
        )
    (tmp_path / "build/target/units.txt").write_text(
        "".join(f"{a:08X} {a + 0x10:08X}\n" for a in bodies)
    )
    (tmp_path / "config").mkdir()
    write_symbols(
        tmp_path / "config/symbols.txt",
        [
            Entry(0x11000, "function", 0, "FUN_00011000", "auto", ""),
            Entry(0x11020, "function", 0, "FUN_00011020", "auto", ""),
            Entry(0x11030, "function", 0, "Load", "string", "string:0x00020000"),
            Entry(0x11050, "function", 0, "XapiInit", "sdk", "sdk"),
            Entry(0x11070, "function", 0, "FUN_00011070", "auto", ""),
        ],
    )
    (tmp_path / "config/functions.csv").write_text(
        "address,status,source,score,detail\n"
        "0x00011070,nonmatching,src/game/a.cpp,50.0,\n"
    )
    assert [(c.address, c.size, c.relocs) for c in candidates(tmp_path, 5, 16)] == [
        (0x11000, 20, 0),
        (0x11030, 20, 1),
    ]
    assert [c.address for c in candidates(tmp_path, 5, 16, 1)] == [0x11030]


# The original slot-0 function at 0x00011010 calls 0x00011000 and returns.
SLOT_CODE = b"\xe8" + (0x11000 - 0x11015).to_bytes(4, "little", signed=True) + b"\xc3"


def deleting_destructor_check(code: bytes, relocs=((1, 6, REL32),), slot=SLOT_CODE):
    rdata = (0x11010).to_bytes(4, "little")
    text = b"\xcc" * 0x10 + slot + b"\xcc" * (0x10 - len(slot))
    tag = (2).to_bytes(4, "little") + bytes(14)
    obj = push_obj(
        [
            ("??_7Foo@@6B@", 0, 2, 0, STATIC),
            ("??_GFoo@@UAEPAXI@Z", 0, 0, 0x20, EXTERNAL),
            ("??_EFoo@@UAEPAXI@Z", 0, 0, 0x20, WEAK_EXTERNAL, tag),
            ("??_GFoo@@UAEPAXI@Z", 0, 3, 0x20, EXTERNAL),
            ("_FUN_00011000", 0, 0, 0x20, EXTERNAL),
        ],
        [
            (".rdata", b"\0\0\0\0", [(0, 3, DIR32)], 0x40000040),
            (".text", code, list(relocs)),
        ],
    )
    return check(obj, rdata=rdata, text=text)


def test_compiler_generated_slot_function_is_checked_against_the_original():
    assert deleting_destructor_check(b"\xe8\0\0\0\0\xc3")[0] == "matched"
    status, _, detail = deleting_destructor_check(b"\xe8\0\0\0\0\xc2\x04\x00")
    assert status == "nonmatching"
    assert "differs from 0x00011010" in detail


def test_a_second_reference_to_a_checked_item_must_expect_the_same_address():
    store_vtable = b"\xc7\x06\0\0\0\0\xc3"
    relocs = ((2, 1, DIR32),)
    same = b"\xc7\x06" + (0x20000).to_bytes(4, "little") + b"\xc3"
    other = b"\xc7\x06" + (0x20004).to_bytes(4, "little") + b"\xc3"
    assert deleting_destructor_check(store_vtable, relocs, same)[0] == "matched"
    status, _, detail = deleting_destructor_check(store_vtable, relocs, other)
    assert status == "nonmatching"
    assert "0x00020000" in detail and "0x00020004" in detail


CLAIM = "// 0x00011000\nvoid f()\n{\n}\n"
UNRESOLVED = "relocation at +0x1: {} names 0 entries in symbols.txt"


# The built f() calls a constructor or destructor that its object does not
# define. The original f() at 0x00011000 calls 0x00011010.
def declared_run(root: Path, callee: str = "??0Foo@@QAE@XZ"):
    obj = build_coff(
        sections=[(".text", CALL, [(1, 1, REL32)])],
        symbols=[
            ("?f@@YAXXZ", 0, 1, 0x20, EXTERNAL),
            (callee, 0, 0, 0x20, EXTERNAL),
        ],
    )
    results, problems = run(root, compile=fake_compile(obj))
    return [(r.status, r.detail) for r in results], problems


def test_call_to_a_declared_constructor_resolves_to_the_stated_address(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::Foo\n" + CLAIM)
    assert declared_run(root) == ([("matched", "")], [])


def test_call_to_a_declared_destructor_resolves_to_the_stated_address(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::~Foo\n" + CLAIM)
    assert declared_run(root, "??1Foo@@QAE@XZ") == ([("matched", "")], [])


def test_declared_constructor_at_another_address_does_not_match(tmp_path):
    root = project(tmp_path, "// declared: 0x00011020 Foo::Foo\n" + CLAIM)
    detail = "relocation at +0x1: built 0x00011020, target 0x00011010"
    assert declared_run(root) == ([("nonmatching", detail)], [])


def test_constructor_without_a_declared_line_does_not_resolve(tmp_path):
    root = project(tmp_path, CLAIM)
    detail = UNRESOLVED.format("??0Foo@@QAE@XZ")
    assert declared_run(root) == ([("nonmatching", detail)], [])


def test_declared_constructor_gives_no_address_to_the_destructor(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::Foo\n" + CLAIM)
    detail = UNRESOLVED.format("??1Foo@@QAE@XZ")
    assert declared_run(root, "??1Foo@@QAE@XZ") == ([("nonmatching", detail)], [])


def test_declared_constructor_gives_no_address_to_a_nested_class(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::Foo\n" + CLAIM)
    detail = UNRESOLVED.format("??0Foo@N@@QAE@XZ")
    assert declared_run(root, "??0Foo@N@@QAE@XZ") == ([("nonmatching", detail)], [])


def test_declared_line_in_an_included_header_is_read(tmp_path):
    root = project(tmp_path, '#include "Foo.h"\n' + CLAIM)
    (root / "src/game/Foo.h").write_text("// declared: 0x00011010 Foo::Foo\n")
    assert declared_run(root) == ([("matched", "")], [])


def test_declared_line_in_a_header_of_a_header_is_read(tmp_path):
    root = project(tmp_path, '#include "Foo.h"\n' + CLAIM)
    (root / "src/game/Foo.h").write_text('#include "base/Base.h"\n')
    (root / "src/game/base").mkdir()
    (root / "src/game/base/Base.h").write_text("// declared: 0x00011010 Foo::Foo\n")
    assert declared_run(root) == ([("matched", "")], [])


def test_header_include_is_read_from_the_folder_of_the_header(tmp_path):
    root = project(tmp_path, '#include "base/Base.h"\n' + CLAIM)
    (root / "src/game/base").mkdir()
    (root / "src/game/base/Base.h").write_text('#include "Foo.h"\n')
    (root / "src/game/base/Foo.h").write_text("// declared: 0x00011010 Foo::Foo\n")
    assert declared_run(root) == ([("matched", "")], [])


def test_headers_that_include_each_other_are_each_read_once(tmp_path):
    root = project(tmp_path, '#include "Foo.h"\n' + CLAIM)
    (root / "src/game/Foo.h").write_text('#include "Bar.h"\n')
    (root / "src/game/Bar.h").write_text(
        '#include "Foo.h"\n// declared: 0x00011010 Foo::Foo\n'
    )
    assert declared_run(root) == ([("matched", "")], [])


def test_include_of_a_file_that_is_not_beside_its_includer_is_skipped(tmp_path):
    lines = '#include "elsewhere.h"\n// declared: 0x00011010 Foo::Foo\n'
    root = project(tmp_path, lines + CLAIM)
    assert declared_run(root) == ([("matched", "")], [])


def test_declared_line_in_a_header_that_is_not_included_is_not_read(tmp_path):
    root = project(tmp_path, CLAIM)
    (root / "src/game/Foo.h").write_text("// declared: 0x00011010 Foo::Foo\n")
    detail = UNRESOLVED.format("??0Foo@@QAE@XZ")
    assert declared_run(root) == ([("nonmatching", detail)], [])


def test_declared_line_takes_only_a_constructor_or_destructor(tmp_path):
    lines = (
        "// declared: 0x00011010 Foo::Bar\n"
        "// declared: 0x00011010 Bar\n"
        "// declared: 0x00011010 Foo::operator new\n"
    )
    root = project(tmp_path, lines + CLAIM)
    start = "src/game/a.cpp:{}: declared takes only a constructor or destructor, not {}"
    assert declared_run(root) == (
        [],
        [
            start.format(1, "Foo::Bar"),
            start.format(2, "Bar"),
            start.format(3, "Foo::operator new"),
        ],
    )


def test_declared_line_without_an_eight_digit_address_is_a_problem(tmp_path):
    root = project(tmp_path, "// declared: 0x11010 Foo::Foo\n" + CLAIM)
    problem = "src/game/a.cpp:1: declared needs an 8-digit 0xADDRESS and a name"
    assert declared_run(root) == ([], [problem])


def test_two_files_can_hold_the_same_declared_line(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::Foo\n" + CLAIM)
    (root / "src/game/b.cpp").write_text("// declared: 0x00011010 Foo::Foo\n")
    assert declared_run(root) == ([("matched", "")], [])


def test_one_declared_name_with_two_addresses_is_a_problem(tmp_path):
    root = project(tmp_path, "// declared: 0x00011010 Foo::Foo\n" + CLAIM)
    (root / "src/game/b.cpp").write_text("// declared: 0x00011020 Foo::Foo\n")
    problem = (
        "Foo::Foo is declared at 0x00011010 in src/game/a.cpp:1 "
        "and at 0x00011020 in src/game/b.cpp:1"
    )
    assert declared_run(root) == ([], [problem])


def test_a_bad_declared_line_in_a_shared_header_is_reported_once(tmp_path):
    root = project(tmp_path, '#include "Foo.h"\n' + CLAIM)
    (root / "src/game/b.cpp").write_text('#include "Foo.h"\n')
    (root / "src/game/Foo.h").write_text("// declared: 0x00011010 Foo::Bar\n")
    problem = (
        "src/game/Foo.h:1: declared takes only a constructor or destructor, "
        "not Foo::Bar"
    )
    assert declared_run(root) == ([], [problem])
