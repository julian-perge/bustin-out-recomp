import subprocess
import sys
from pathlib import Path

from bodecomp.findings import (
    check,
    commit_exists,
    commit_known,
    parse,
    pre_public_commits,
    summary,
)

ROOT = Path(__file__).resolve().parent.parent

GOOD = """# Findings

Intro text without second-level headings.

## F-0001 Library functions were cut short
- Status: fixed (abc1234)
- Checked: test test_x

## F-0002 Apt is in the Xbox build
- Status: confirmed

## F-0003 Code outside functions
- Status: open
- Next: M2

## F-0004 Thunk names
- Status: active (namer, 2026-10-11)

## F-0005 Old claim
- Status: rejected
"""


def git_repo(path: Path) -> str:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(path), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    (path / "a.txt").write_text("a\n")
    git("add", "a.txt")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "a")
    return git("rev-parse", "HEAD")


def test_parse_reads_ids_titles_and_statuses():
    findings, errors = parse(GOOD)
    assert errors == []
    assert [(f.id, f.status) for f in findings] == [
        ("F-0001", "fixed"),
        ("F-0002", "confirmed"),
        ("F-0003", "open"),
        ("F-0004", "active"),
        ("F-0005", "rejected"),
    ]
    assert findings[0].commit == "abc1234"
    assert (findings[3].owner, findings[3].date) == ("namer", "2026-10-11")
    assert findings[1].title == "Apt is in the Xbox build"
    assert findings[1].line == 9


def test_unknown_status_is_an_error_with_its_line():
    _, errors = parse("## F-0001 Title\n- Status: done\n")
    assert errors == ["line 2: F-0001 has an invalid status: done"]


def test_missing_status_is_an_error():
    _, errors = parse("## F-0001 Title\n- Checked: test x\n")
    assert errors == ["line 1: F-0001 has no Status line"]


def test_malformed_heading_is_an_error_not_skipped():
    _, errors = parse("## F-12 Short id\n- Status: open\n")
    assert errors == [
        "line 1: every '## ' heading must be '## F-NNNN <title>': ## F-12 Short id"
    ]


def test_lowercase_heading_is_an_error():
    _, errors = parse("## f-0003 Lowercase\n- Status: open\n")
    assert len(errors) == 1 and errors[0].startswith("line 1: every '## ' heading")


def test_status_line_tolerates_trailing_spaces():
    findings, errors = parse("## F-0001 A\n- Status: open   \n")
    assert errors == [] and findings[0].status == "open"


def test_duplicate_ids_are_errors():
    text = "## F-0001 A\n- Status: open\n\n## F-0001 B\n- Status: open\n"
    findings, errors = parse(text)
    assert errors == []
    assert check(findings, lambda sha: True) == ["line 4: F-0001 is used twice"]


def test_fixed_commit_must_exist(tmp_path):
    sha = git_repo(tmp_path)
    text = (
        f"## F-0001 A\n- Status: fixed ({sha[:7]})\n\n"
        "## F-0002 B\n- Status: fixed (1234567)\n"
    )
    findings, _ = parse(text)
    errors = check(findings, lambda c: commit_exists(c, tmp_path))
    assert errors == ["line 4: F-0002 names commit 1234567, which does not exist"]


def test_fixed_commit_from_the_pre_public_list_is_known(tmp_path):
    git_repo(tmp_path)
    listed = tmp_path / "pre-public-commits.txt"
    listed.write_text("# hashes\n\nabcdef0123456789abcdef0123456789abcdef01\n")
    text = (
        "## F-0001 A\n- Status: fixed (abcdef0)\n\n"
        "## F-0002 B\n- Status: fixed (1234567)\n"
    )
    findings, _ = parse(text)
    known = pre_public_commits(listed)
    errors = check(findings, lambda c: commit_known(c, tmp_path, known))
    assert errors == ["line 4: F-0002 names commit 1234567, which does not exist"]


def test_missing_pre_public_list_is_empty(tmp_path):
    assert pre_public_commits(tmp_path / "absent.txt") == []


def test_check_command_reads_the_pre_public_list(tmp_path):
    git_repo(tmp_path)
    findings = tmp_path / "findings.md"
    findings.write_text("## F-0001 A\n- Status: fixed (abcdef0)\n")
    listed = tmp_path / "listed.txt"
    listed.write_text("abcdef0123456789abcdef0123456789abcdef01\n")
    other = tmp_path / "other.txt"
    other.write_text("0000000123456789abcdef0123456789abcdef01\n")

    def run(pre_public: Path) -> int:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "bodecomp.findings",
                "check",
                "--path",
                str(findings),
                "--pre-public",
                str(pre_public),
            ],
            cwd=ROOT,
            capture_output=True,
        ).returncode

    assert run(listed) == 0
    assert run(other) == 1


def test_summary_lists_open_and_active_in_id_order():
    findings, _ = parse(GOOD)
    assert summary(findings, limit=10) == [
        "F-0003 open: Code outside functions",
        "F-0004 active (namer, 2026-10-11): Thunk names",
    ]


def test_summary_limit_says_how_many_more():
    text = "".join(f"## F-{i:04d} T{i}\n- Status: open\n\n" for i in range(1, 6))
    findings, _ = parse(text)
    assert summary(findings, limit=2) == [
        "F-0001 open: T1",
        "F-0002 open: T2",
        "... and 3 more: rg -n 'Status: (open|active)' docs/FINDINGS.md",
    ]


def test_check_command_exit_codes(tmp_path):
    git_repo(tmp_path)
    good = tmp_path / "good.md"
    good.write_text("## F-0001 A\n- Status: open\n")
    bad = tmp_path / "bad.md"
    bad.write_text("## F-0001 A\n- Status: maybe\n")

    def run(path: Path) -> int:
        return subprocess.run(
            [sys.executable, "-m", "bodecomp.findings", "check", "--path", str(path)],
            cwd=ROOT,
            capture_output=True,
        ).returncode

    assert run(good) == 0
    assert run(bad) == 1


def test_near_miss_headings_are_errors():
    for heading in ("### F-0002 B", "##F-0002 B", " ## F-0002 B"):
        _, errors = parse(f"{heading}\n- Status: open\n")
        assert len(errors) == 1, heading
        assert errors[0].startswith("line 1: every '## ' heading"), heading


def test_second_status_line_is_an_error():
    text = "## F-0001 A\n- Status: open\n- Status: fixed (deadbee)\n"
    findings, errors = parse(text)
    assert errors == ["line 3: F-0001 has a second Status line"]
    assert [f.status for f in findings] == ["open"]
