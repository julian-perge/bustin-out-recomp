from pathlib import Path

import pytest

from bodecomp.ledger import main, render, status
from bodecomp.symbols import Entry, read_symbols, write_symbols

ROOT = Path(__file__).resolve().parent.parent


def fn(address, tier, evidence, size=16, kind="function"):
    return Entry(address, kind, size, f"FUN_{address:08x}", tier, evidence)


def test_evidence_forms_map_to_statuses():
    lib = "lib:xapilib.lib:obj\\i386\\synch.obj; was:CreateEventA"
    assert status(fn(1, "sdk", lib)) == "sdk"
    ambiguous = "lib-ambiguous(3):_PulseEvent@4,_ReleaseMutex@4,_SetEvent@4"
    assert status(fn(2, "sdk", ambiguous)) == "sdk-ambiguous"
    assert status(fn(3, "sdk", "section:D3D")) == "sdk-section"
    assert status(fn(4, "sdk", "xbe-loader")) == "sdk-other"
    assert status(fn(5, "sdk", "ghidra-fid")) == "sdk-other"
    assert status(fn(6, "auto", "")) == "open"


def test_unknown_tier_is_an_error_naming_the_address():
    with pytest.raises(ValueError, match=r"0x00000007 .*'xyz'"):
        status(fn(7, "xyz", "xyz:Foo"))


def test_game_name_tiers_are_their_own_statuses():
    assert status(fn(1, "gc", "gc:strings+callgraph")) == "gc"
    assert status(fn(2, "string", "string:foo.cpp")) == "string"
    assert status(fn(3, "matched", "src/sims/ESimsApp.cpp")) == "matched"


def test_totals_count_functions_only():
    entries = [
        fn(1, "sdk", "lib:a", size=10),
        fn(2, "auto", "", size=30),
        fn(3, "sdk", "xbe-loader", size=0, kind="data"),
    ]
    text = render(entries)
    assert "| **all** | | **2** | | **40** | |" in text
    assert "Data labels in `symbols.txt`: 1 (not counted above)." in text
    assert "| `sdk` | " in text and "| 1 | 50.0% | 10 | 25.0% |" in text


def test_render_does_not_depend_on_entry_order():
    entries = [fn(1, "sdk", "lib:a"), fn(2, "auto", ""), fn(3, "sdk", "section:D3D")]
    assert render(entries) == render(list(reversed(entries)))


def test_real_symbols_total_equals_the_function_entries():
    entries = read_symbols(ROOT / "config/symbols.txt")
    functions = sum(1 for e in entries if e.kind == "function")
    assert f"| **all** | | **{functions:,}** |" in render(entries)


def test_check_flags_a_stale_ledger(tmp_path):
    symbols, out = tmp_path / "symbols.txt", tmp_path / "LEDGER.md"
    write_symbols(symbols, [fn(1, "sdk", "lib:a"), fn(2, "auto", "")])
    args = ["--symbols", str(symbols), "--out", str(out)]
    assert main(args) == 0
    assert main([*args, "--check"]) == 0
    out.write_text(out.read_text() + "edited\n")
    assert main([*args, "--check"]) == 1


def test_game_table_reports_each_name_tier_share():
    entries = [
        fn(1, "sdk", "lib:a", size=100),
        fn(2, "gc", "gc:strings+callgraph", size=10),
        fn(3, "string", "string:foo.cpp", size=10),
        fn(4, "matched", "src/sims/ESimsApp.cpp", size=10),
        fn(5, "auto", "", size=10),
    ]
    text = render(entries)
    assert "## Game functions by name tier" in text
    assert "| `matched` | 1 | 25.0% | 10 | 25.0% |" in text
    assert "| `gc` | 1 | 25.0% | 10 | 25.0% |" in text
    assert "| `string` | 1 | 25.0% | 10 | 25.0% |" in text
    assert "| `auto` | 1 | 25.0% | 10 | 25.0% |" in text
    assert "| **all game** | **4** | | **40** | |" in text
    assert "Named game functions: 3 of 4 (75.0%)." in text


def test_no_game_functions_gives_zero_shares():
    text = render([fn(1, "sdk", "lib:a")])
    assert "| `auto` | 0 | 0.0% | 0 | 0.0% |" in text
    assert "Named game functions: 0 of 0 (0.0%)." in text


def test_match_status_comes_from_functions_csv_whatever_the_name_tier():
    entries = [
        fn(1, "auto", "", size=10),
        fn(2, "auto", "", size=30),
        fn(3, "string", "string:0x00020000", size=60),
        fn(4, "sdk", "lib:a", size=100),
    ]
    matches = {1: ("matched", "src/game/a.cpp"), 3: ("parked", "src/game/b.cpp")}
    text = render(entries, matches)
    assert "| `matched` | 1 | 33.3% | 10 | 10.0% |" in text
    assert "| `parked` | 1 | 33.3% | 60 | 60.0% |" in text
    assert "| `open` | 1 | 33.3% | 30 | 30.0% |" in text.split("by match status")[1]
