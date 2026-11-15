import pytest

from bodecomp.readme import END, START, bar, main, render, replace
from bodecomp.symbols import Entry, write_symbols


def fn(address, tier, evidence, size=16):
    return Entry(address, "function", size, f"FUN_{address:08x}", tier, evidence)


ENTRIES = [
    fn(1, "auto", "", size=10),
    fn(2, "auto", "", size=30),
    fn(3, "string", "string:a.cpp", size=60),
    fn(4, "sdk", "lib:xapilib.lib:obj", size=40),
    fn(5, "sdk", "section:D3D", size=60),
]


def test_bar_shows_any_progress_and_stays_ascii():
    assert bar(0, 100) == "[" + "-" * 20 + "]"
    assert bar(1, 10_000) == "[#" + "-" * 19 + "]"
    assert bar(5, 10, width=4) == "[##--]"


def test_render_counts_matched_named_and_sdk():
    text = render(ENTRIES, {1: ("matched", "src/a.cpp"), 2: ("parked", "src/b.cpp")})
    assert text.startswith(START) and text.endswith(END)
    assert "| Game code matched from C++ | 1 / 3 | 10.00% |" in text
    assert "| Game code named | 1 / 3 | 60.00% |" in text
    assert "| Xbox SDK named from a unique XDK library match | 1 / 2 | 40.00% |" in text
    assert "1 matched, 0 nonmatching, 1 parked." in text
    assert text.isascii()


def test_replace_keeps_text_around_the_block_and_requires_markers():
    old = f"intro\n{START}\nold\n{END}\nafter\n"
    assert (
        replace(old, f"{START}\nnew\n{END}") == f"intro\n{START}\nnew\n{END}\nafter\n"
    )
    with pytest.raises(ValueError):
        replace("no markers", "x")


def test_main_rewrites_only_the_block(tmp_path):
    symbols, readme = tmp_path / "symbols.txt", tmp_path / "README.md"
    write_symbols(symbols, ENTRIES)
    readme.write_text(f"# Title\n\n{START}\n{END}\n\nTail.\n")
    assert (
        main(
            [
                "--symbols",
                str(symbols),
                "--functions",
                str(tmp_path / "none.csv"),
                "--readme",
                str(readme),
            ]
        )
        == 0
    )
    text = readme.read_text()
    assert text.startswith("# Title\n\n" + START) and text.endswith(END + "\n\nTail.\n")
    assert "| Game code matched from C++ | 0 / 3 | 0.00% |" in text
