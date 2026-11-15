import pytest

from bodecomp.names import batches, check, clear_name, problems, set_name, stated
from bodecomp.strings import StringRef
from bodecomp.symbols import Entry

REFS = {
    0x33E30: [StringRef(0x2E6000, "system.cnf")],
    0x11610: [StringRef(0x2E5000, "The Sims For PS2")],
}


def entries():
    return [
        Entry(0x11000, "function", 20, "_sprintf", "sdk", "lib:libcmt.lib:sprintf.obj"),
        Entry(0x11610, "function", 16, "FUN_00011610", "auto", ""),
        Entry(0x33E30, "function", 90, "FUN_00033e30", "auto", ""),
    ]


def test_set_records_a_string_name_with_its_evidence():
    out = set_name(
        entries(), REFS, 0x33E30, "ECheats::ReadCheatsFile", "string:0x002E6000"
    )
    assert out[2] == Entry(
        0x33E30,
        "function",
        90,
        "ECheats::ReadCheatsFile",
        "string",
        "string:0x002E6000",
    )


def test_set_refuses_a_name_in_use():
    with pytest.raises(ValueError, match="already used"):
        set_name(entries(), REFS, 0x33E30, "_sprintf", "string:0x002E6000")


def test_set_refuses_evidence_the_function_does_not_reference():
    with pytest.raises(ValueError, match="does not reference"):
        set_name(entries(), REFS, 0x33E30, "ReadCheatsFile", "string:0x002E5000")


def test_set_refuses_an_sdk_function():
    with pytest.raises(ValueError, match="tier sdk"):
        set_name(entries(), REFS, 0x11000, "FormatText", "string:0x002E6000")


def test_set_refuses_malformed_names_and_evidence():
    with pytest.raises(ValueError, match="not a valid string-tier name"):
        set_name(entries(), REFS, 0x33E30, "Read Cheats", "string:0x002E6000")
    with pytest.raises(ValueError, match="not a valid string-tier name"):
        set_name(entries(), REFS, 0x33E30, "FUN_00033e30", "string:0x002E6000")
    with pytest.raises(ValueError, match="evidence"):
        set_name(entries(), REFS, 0x33E30, "ReadCheatsFile", "system.cnf")


def test_clear_restores_the_auto_name():
    named = set_name(entries(), REFS, 0x33E30, "ReadCheatsFile", "string:0x002E6000")
    assert clear_name(named, 0x33E30)[2] == entries()[2]


def test_clear_refuses_a_name_that_is_not_string_tier():
    with pytest.raises(ValueError, match="tier sdk"):
        clear_name(entries(), 0x11000)


def test_check_reports_string_names_whose_evidence_no_longer_holds():
    named = set_name(entries(), REFS, 0x33E30, "ReadCheatsFile", "string:0x002E6000")
    assert check(named, REFS) == []
    assert check(named, {}) == [
        "0x00033E30 ReadCheatsFile: cites 0x002E6000, which it does not reference"
    ]


def test_problems_accepts_a_destructor_name():
    entry = Entry(0x11610, "function", 16, "EApp::~EApp", "string", "string:0x002E5000")
    assert problems(entry, REFS) == []


def test_stated_names_a_function_whose_string_states_its_name():
    refs = {
        0x20000: [
            StringRef(0x2E7000, "CreateASimBaseState::Update()"),
            StringRef(0x2E7020, "CreateASimBaseState::Update()"),
            StringRef(0x2E7040, "Sim::Table"),
        ]
    }
    names = [Entry(0x20000, "function", 50, "FUN_00020000", "auto", "")]
    assert stated(names, refs) == [
        (0x20000, "CreateASimBaseState::Update", [0x2E7000, 0x2E7020])
    ]


def test_stated_skips_a_name_two_functions_state():
    refs = {
        0x20000: [StringRef(0x2E7000, "EResourceManager::AddRef() tried to load")],
        0x20100: [StringRef(0x2E7000, "EResourceManager::AddRef() tried to load")],
    }
    names = [
        Entry(0x20000, "function", 50, "FUN_00020000", "auto", ""),
        Entry(0x20100, "function", 50, "FUN_00020100", "auto", ""),
    ]
    assert stated(names, refs) == []


def test_stated_skips_a_function_whose_strings_state_two_names():
    refs = {
        0x20000: [
            StringRef(0x2E7000, "A::Update()"),
            StringRef(0x2E7020, "B::Update()"),
        ]
    }
    names = [Entry(0x20000, "function", 50, "FUN_00020000", "auto", "")]
    assert stated(names, refs) == []


def test_stated_leaves_named_functions_alone():
    refs = {0x11000: [StringRef(0x2E7000, "A::Update()")]}
    names = [Entry(0x11000, "function", 50, "_sprintf", "sdk", "lib:x")]
    assert stated(names, refs) == []


def test_batches_keep_their_numbering_after_naming():
    names = [
        Entry(
            0x20000 + i * 16, "function", 8, f"FUN_{0x20000 + i * 16:08x}", "auto", ""
        )
        for i in range(5)
    ]
    names.append(Entry(0x10000, "function", 8, "_sprintf", "sdk", "lib:x"))
    refs = {
        e.address: [StringRef(0x2E7000 + i, f"text{i}")] for i, e in enumerate(names)
    }
    before = batches(names, refs, size=2)
    renamed = set_name(names, refs, 0x20000, "First", "string:0x002E7000")
    after = batches(renamed, refs, size=2)
    assert [[e.address for e in b] for b in before] == [
        [e.address for e in b] for b in after
    ]
    assert [len(b) for b in before] == [2, 2, 1]
    assert all(e.tier != "sdk" for b in before for e in b)


@pytest.fixture
def root(tmp_path):
    (tmp_path / "src/sims").mkdir(parents=True)
    for name in ("ECheats.cpp", "Foo.cpp"):
        (tmp_path / "src/sims" / name).write_text("")
    listed(tmp_path, "matched", "src/sims/ECheats.cpp")
    return tmp_path


def listed(root, status, source):
    (root / "config").mkdir(exist_ok=True)
    (root / "config/functions.csv").write_text(
        f"address,status,source,score,detail\n0x00033E30,{status},{source},100.0,\n"
    )


def test_set_records_a_matched_name_with_its_source(root):
    name = "?ReadCheatsFile@ECheats@@QAEXXZ"
    out = set_name(entries(), REFS, 0x33E30, name, "src/sims/ECheats.cpp", root)
    assert out[2] == Entry(
        0x33E30, "function", 90, name, "matched", "src/sims/ECheats.cpp"
    )


def test_set_matched_keeps_the_replaced_string_name(root):
    named = set_name(entries(), REFS, 0x33E30, "ReadCheatsFile", "string:0x002E6000")
    out = set_name(
        named, REFS, 0x33E30, "_ReadCheatsFile", "src/sims/ECheats.cpp", root
    )
    assert out[2].evidence == "src/sims/ECheats.cpp was:ReadCheatsFile"
    assert check(out, REFS, root) == []


def test_set_matched_replaces_a_gc_name_but_not_sdk_or_matched(root):
    gc = [*entries()[:2], Entry(0x33E30, "function", 90, "Foo", "gc", "gc:x")]
    listed(root, "matched", "src/sims/Foo.cpp")
    out = set_name(gc, REFS, 0x33E30, "_Foo", "src/sims/Foo.cpp", root)
    assert out[2].evidence == "src/sims/Foo.cpp was:Foo"
    with pytest.raises(ValueError, match="tier matched"):
        set_name(out, REFS, 0x33E30, "_Bar", "src/sims/Foo.cpp", root)
    with pytest.raises(ValueError, match="tier sdk"):
        set_name(entries(), REFS, 0x11000, "_Bar", "src/sims/Foo.cpp", root)


def test_set_gc_name_needs_matched_evidence(root):
    gc = [*entries()[:2], Entry(0x33E30, "function", 90, "Foo", "gc", "gc:x")]
    with pytest.raises(ValueError, match="tier gc"):
        set_name(gc, REFS, 0x33E30, "Bar", "string:0x002E6000")


def test_set_refuses_malformed_matched_names_and_sources(root):
    with pytest.raises(ValueError, match="not a valid matched name"):
        set_name(
            entries(), REFS, 0x33E30, "ECheats::Read", "src/sims/ECheats.cpp", root
        )
    with pytest.raises(ValueError, match="not a src/"):
        set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/ECheats.h", root)
    with pytest.raises(ValueError, match="not a src/"):
        set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/ECheats.cpp was:X", root)


def test_check_reports_malformed_matched_entries(root):
    bad = Entry(0x11610, "function", 16, "Read Cheats", "matched", "ECheats.cpp")
    assert len(check([bad], REFS, root)) == 2


def test_set_and_check_refuse_a_missing_source(root):
    with pytest.raises(ValueError, match="src/sims/Gone.cpp does not exist"):
        set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/Gone.cpp", root)
    gone = Entry(0x11610, "function", 16, "_Read", "matched", "src/sims/Gone.cpp")
    assert check([gone], REFS, root)[0] == (
        "0x00011610 _Read: src/sims/Gone.cpp does not exist"
    )


def test_set_matched_needs_a_matched_row_from_the_same_source(root):
    with pytest.raises(ValueError, match="does not list it as matched"):
        set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/Foo.cpp", root)
    listed(root, "nonmatching", "src/sims/ECheats.cpp")
    with pytest.raises(ValueError, match="does not list it as matched"):
        set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/ECheats.cpp", root)


def test_check_reports_a_matched_name_that_no_longer_matches(root):
    out = set_name(entries(), REFS, 0x33E30, "_Read", "src/sims/ECheats.cpp", root)
    assert check(out, REFS, root) == []
    listed(root, "nonmatching", "src/sims/ECheats.cpp")
    assert len(check(out, REFS, root)) == 1
