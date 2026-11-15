from bodecomp.gaps import Gap, candidates, find_gaps, main, summarize
from bodecomp.symbols import Entry, write_symbols
from tests.xbebuild import build_xbe


def test_gaps_are_the_text_bytes_no_function_covers():
    functions = [(0x1010, 0x10), (0x1018, 0x4), (0x1030, 0x8)]
    assert find_gaps(0x1000, 0x1040, functions) == [
        Gap(0x1000, 0x1010),
        Gap(0x101C, 0x1030),
        Gap(0x1038, 0x1040),
    ]


def test_functions_outside_text_are_ignored_and_straddlers_clipped():
    functions = [(0x0F00, 0x10), (0x0FF8, 0x10), (0x1040, 0x10), (0x1038, 0x20)]
    assert find_gaps(0x1000, 0x1040, functions) == [Gap(0x1008, 0x1038)]


def test_candidate_needs_padding_before_and_code_at_an_aligned_address():
    text = bytearray(b"\xcc" * 0x40)
    text[0x10] = 0x55
    text[0x1F] = 0xC3
    text[0x20] = 0x55
    text[0x28] = 0x55
    assert candidates(bytes(text), 0x1000, [Gap(0x1000, 0x1040)]) == [0x1010]


def test_candidates_stay_inside_gaps_and_round_the_gap_start_up():
    text = bytearray(b"\xcc" * 0x40)
    text[0x10] = 0x55
    assert candidates(bytes(text), 0x1000, [Gap(0x1018, 0x1040)]) == []
    assert candidates(bytes(text), 0x1000, [Gap(0x1001, 0x1040)]) == [0x1010]


def test_summary_counts_padding_only_gaps_and_non_padding_bytes():
    text = bytearray(b"\xcc" * 0x30)
    text[0x12] = 0x55
    text[0x13] = 0xC3
    text[0x25] = 0xC3
    gaps = [Gap(0x1000, 0x1010), Gap(0x1010, 0x1020), Gap(0x1020, 0x1030)]
    s = summarize(bytes(text), 0x1000, gaps)
    assert (s.gaps, s.gap_bytes, s.padding_gaps, s.code_bytes) == (3, 0x30, 1, 3)
    assert s.largest == [(Gap(0x1010, 0x1020), 2), (Gap(0x1020, 0x1030), 1)]


TEXT = (
    b"\x90" * 12
    + b"\xc3"
    + b"\xcc" * 3
    + b"\xc3"
    + b"\xcc" * 15
    + b"\x90" * 15
    + b"\xc3"
    + b"\xcc" * 16
)


def inputs(tmp_path):
    xbe = tmp_path / "default.xbe"
    sections = [(".text", 0x11000, TEXT), ("D3D", 0x12000, b"\xc3" * 16)]
    xbe.write_bytes(build_xbe(sections, [], 0x45410091, 0x11000))
    symbols = tmp_path / "symbols.txt"
    write_symbols(
        symbols,
        [
            Entry(0x11000, "function", 13, "A", "sdk", "lib:a"),
            Entry(0x11010, "data", 0, "x", "sdk", "xbe-loader"),
            Entry(0x11020, "function", 16, "FUN_00011020", "auto", ""),
            Entry(0x12000, "function", 16, "D", "sdk", "section:D3D"),
        ],
    )
    return ["--xbe", str(xbe), "--symbols", str(symbols)]


def test_candidates_command_writes_hex_addresses(tmp_path):
    out = tmp_path / "candidates.txt"
    assert main(["candidates", *inputs(tmp_path), "--out", str(out)]) == 0
    assert out.read_text() == "00011010\n"


def test_starts_command_lists_every_function_in_every_section(tmp_path):
    out = tmp_path / "starts.txt"
    assert main(["starts", *inputs(tmp_path), "--out", str(out)]) == 0
    assert out.read_text() == "00011000\n00011020\n00012000\n"


def test_report_command_prints_the_totals(tmp_path, capsys):
    assert main(["report", *inputs(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "gaps 2, bytes 35, padding-only gaps 1, non-padding bytes 1" in out
    assert "0x0001100D-0x00011020 1 non-padding bytes" in out


def test_a_function_span_stops_at_the_next_function_start():
    functions = [(0x1000, 0x40), (0x1010, 0x10)]
    assert find_gaps(0x1000, 0x1040, functions) == [Gap(0x1020, 0x1040)]
