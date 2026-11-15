from pathlib import Path

from bodecomp.cl import CompileResult
from bodecomp.coff import Reloc
from bodecomp.m0 import (
    FLAG_SETS,
    Candidate,
    compare,
    load_candidates,
    render_report,
    run_matrix,
    write_report,
)
from bodecomp.xbe import Xbe
from tests.coffbuild import build_coff
from tests.xbebuild import build_xbe

TARGET = b"\x8b\x41\x08\xc3"


def test_identical_bytes_match():
    assert compare(TARGET, TARGET, ()).status == "match"


def test_trailing_int3_padding_still_matches():
    assert compare(TARGET, TARGET + b"\xcc\xcc", ()).status == "match"


def test_trailing_real_code_is_a_mismatch():
    verdict = compare(TARGET, TARGET + b"\x90\xc3", ())
    assert verdict.status == "mismatch"
    assert "+0x4" in verdict.detail


def test_first_difference_is_reported():
    verdict = compare(TARGET, b"\x8b\x41\x0c\xc3", ())
    assert verdict.status == "mismatch"
    assert "+0x2" in verdict.detail


def test_relocations_disqualify_the_candidate():
    verdict = compare(TARGET, TARGET, (Reloc(1, "_g_x", 6),))
    assert verdict.status == "has-relocs"
    assert "_g_x" in verdict.detail


def test_flag_sets_cover_the_matrix():
    assert len(FLAG_SETS) == 36
    assert FLAG_SETS["O2"] == ("/O2",)
    assert FLAG_SETS["O1-Oy--G7"] == ("/O1", "/Oy-", "/G7")
    assert FLAG_SETS["O2-G6-SSE"] == ("/O2", "/G6", "/arch:SSE")


def test_load_candidates(tmp_path):
    csv = tmp_path / "c.csv"
    csv.write_text("address,size,source,symbol\n0x00011000,4,src/m0/a.cpp,fn_a\n")
    assert load_candidates(csv) == [Candidate(0x11000, 4, Path("src/m0/a.cpp"), "fn_a")]


def fake_compiler(outputs: dict[str, bytes | None]):
    def compile_stub(root, source, output, flags):
        payload = outputs[" ".join(flags)]
        if payload is None:
            return CompileResult(
                False,
                output,
                "a.cpp\nsrc\\m0\\a.cpp(3) : error C2143: syntax error : missing ';'\n",
            )
        (root / output).parent.mkdir(parents=True, exist_ok=True)
        (root / output).write_bytes(payload)
        return CompileResult(True, output, "")

    return compile_stub


def obj_with(code: bytes) -> bytes:
    return build_coff(
        sections=[(".text", code, [])],
        symbols=[("?fn_a@@YAHXZ", 0, 1, 0x20, 2)],
    )


def test_matrix_keeps_going_after_a_compile_error(tmp_path):
    xbe = Xbe.parse(
        build_xbe([(".text", 0x11000, TARGET)], [], title_id=1, entry=0x11000)
    )
    candidates = [Candidate(0x11000, 4, Path("src/m0/a.cpp"), "fn_a")]
    flag_sets = {"broken": ("/Obroken",), "good": ("/O2",)}
    results = run_matrix(
        tmp_path,
        candidates,
        xbe,
        flag_sets,
        compile=fake_compiler({"/Obroken": None, "/O2": obj_with(TARGET)}),
    )
    assert results["broken"][0x11000].status == "compile-error"
    assert "C2143" in results["broken"][0x11000].detail
    assert results["good"][0x11000].status == "match"

    report = render_report(results, candidates)
    assert "| good | 1/1 |" in report
    assert "| broken | 0/1 |" in report


def test_rewriting_the_report_keeps_the_written_decision(tmp_path):
    path = tmp_path / "m0-results.md"
    path.write_text("# M0 results\n\nold table\n\n## Decision\n\nKeep this.\n")
    write_report(path, "# M0 results\n\nnew table\n")
    text = path.read_text()
    assert "new table" in text
    assert "old table" not in text
    assert text.endswith("## Decision\n\nKeep this.\n")


def test_first_report_has_no_decision_yet(tmp_path):
    path = tmp_path / "m0-results.md"
    write_report(path, "# M0 results\n\nnew table\n")
    assert path.read_text() == "# M0 results\n\nnew table\n"
