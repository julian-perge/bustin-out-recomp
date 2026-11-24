import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from bodecomp import overnight
from bodecomp.overnight import GATE, LEDGER_CHECK, STALLED, Machine, main
from bodecomp.symbols import Entry, write_symbols
from bodecomp.sync import write_stamp

T0 = datetime(2026, 11, 25, 22, 0, tzinfo=UTC)
HEADER = "address,status,source,score,detail\n"
XBE_BYTES = b"XBEH fake image"


def git(root: Path, *args: str, when: datetime = T0) -> str:
    stamp = f"@{int(when.timestamp())} +0000"
    env = {
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": str(root),
    }
    done = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return done.stdout


def functions(root: Path, matched: int, parked: int) -> None:
    rows = [f"0x{0x10000 + i:08X},matched,src/a.cpp,100.0,\n" for i in range(matched)]
    rows += [f"0x{0x20000 + i:08X},parked,src/b.cpp,50.0,\n" for i in range(parked)]
    (root / "config/functions.csv").write_text(HEADER + "".join(rows))


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    functions(root, 3, 1)
    (root / ".gitignore").write_text("/build/\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "first", when=T0 - timedelta(days=2))
    origin = tmp_path / "origin.git"
    git(root, "clone", "-q", "--bare", str(root), str(origin))
    git(root, "remote", "add", "origin", str(origin))
    git(root, "fetch", "-q", "origin")
    return root


class Clock:
    def __init__(self, when: datetime):
        self.when = when

    def __call__(self) -> datetime:
        return self.when


class Fakes:
    """Runs git for real, and answers gh and the gate commands from a table."""

    def __init__(self, root: Path):
        self.root = root
        self.calls: list[tuple[str, ...]] = []
        self.answers: dict[tuple[str, ...], tuple[int, str, str]] = {}
        self.gh_issues = "[]"
        self.pr_url = "https://github.com/o/r/pull/1"
        self.pr_head: str | None = None

    def __call__(self, cmd) -> tuple[int, str, str]:
        cmd = tuple(cmd)
        self.calls.append(cmd)
        if cmd in self.answers:
            return self.answers[cmd]
        if cmd[0] == "git":
            return overnight.shell(self.root)(cmd)
        if cmd in (*GATE, LEDGER_CHECK):
            return 0, "ok\n", ""
        if cmd[:3] == ("gh", "issue", "list"):
            return 0, self.gh_issues, ""
        if cmd[:3] == ("gh", "pr", "view"):
            head = self.pr_head or git(self.root, "rev-parse", "HEAD").strip()
            return 0, json.dumps({"url": self.pr_url, "headRefOid": head}), ""
        if cmd[:2] in (("gh", "auth"), ("gh", "pr")):
            return 0, "", ""
        raise AssertionError(f"unexpected command {cmd}")


def machine(root: Path, clock: Clock, fakes: Fakes, up: bool = True) -> Machine:
    return Machine(root=root, run=fakes, now=clock, server_up=lambda: up)


def run_cli(capsys, m: Machine, *argv: str) -> tuple[int, str]:
    code = main(list(argv), machine=m)
    return code, capsys.readouterr().out


def started(repo, capsys, limit="8h"):
    clock, fakes = Clock(T0), Fakes(repo)
    m = machine(repo, clock, fakes)
    code, _ = run_cli(capsys, m, "start", limit)
    assert code == 0
    return m, clock, fakes


def test_durations():
    assert overnight.parse_duration("8h") == 480
    assert overnight.parse_duration("90m") == 90
    assert overnight.parse_duration("1h30m") == 90
    for bad in ("", "0h", "8", "h", "8x"):
        with pytest.raises(Exception, match="duration"):
            overnight.parse_duration(bad)
    assert overnight.duration(0) == "0m"
    assert overnight.duration(192) == "3h12m"
    assert overnight.duration(480) == "8h"


def test_start_makes_the_run_branch_and_writes_the_run(repo, capsys):
    started(repo, capsys)
    run = json.loads((repo / "build/overnight/run.json").read_text())
    assert run["start"] == "2026-11-25T22:00:00+00:00"
    assert run["limit_minutes"] == 480
    assert run["branch"] == "match/night-2026-11-25"
    assert run["base"] == git(repo, "rev-parse", "main").strip()
    assert (run["matched_at_start"], run["parked_at_start"]) == (3, 1)
    assert run["ended"] is None
    assert git(repo, "branch", "--show-current").strip() == "match/night-2026-11-25"


def test_start_run_twice_keeps_the_first_start_time(repo, capsys):
    m, clock, _ = started(repo, capsys)
    first = (repo / "build/overnight/run.json").read_text()
    clock.when = T0 + timedelta(minutes=10)
    code, out = run_cli(capsys, m, "start", "1h")
    assert code == 0
    assert "a run is live, nothing changed" in out
    assert "elapsed: 10m of 8h" in out
    assert (repo / "build/overnight/run.json").read_text() == first


def test_start_after_an_ended_run_changes_nothing(repo, capsys):
    m, clock, _ = started(repo, capsys)
    assert run_cli(capsys, m, "finish")[0] == 0
    ended = (repo / "build/overnight/run.json").read_text()
    code, out = run_cli(capsys, m, "start", "8h")
    assert code == 1
    assert "has ended; to start a new run:" in out
    assert "delete build/overnight/" in out
    assert (repo / "build/overnight/run.json").read_text() == ended


def status_at(capsys, m, clock, minutes):
    clock.when = T0 + timedelta(minutes=minutes)
    code, out = run_cli(capsys, m, "status")
    assert code == 0
    return out


def test_status_prints_wrap_up_at_85_percent(repo, capsys):
    m, clock, _ = started(repo, capsys)
    assert "wrap up" not in status_at(capsys, m, clock, 407)
    out = status_at(capsys, m, clock, 408)
    assert "wrap up: start no new batch" in out
    assert "remaining: 1h12m" in out


def test_status_prints_remaining_0m_at_the_limit(repo, capsys):
    m, clock, _ = started(repo, capsys)
    assert "remaining: 1m" in status_at(capsys, m, clock, 479)
    for minutes in (480, 600):
        out = status_at(capsys, m, clock, minutes)
        assert "remaining: 0m" in out
        assert "wrap up: start no new batch" in out


def test_status_prints_the_stall_line_after_30_minutes_with_no_commit(repo, capsys):
    m, clock, _ = started(repo, capsys)
    out = status_at(capsys, m, clock, 30)
    assert "minutes since last commit or journal line: 30" in out
    assert STALLED not in out
    assert STALLED in status_at(capsys, m, clock, 31)
    (repo / "note.txt").write_text("x")
    git(repo, "add", "note.txt")
    git(repo, "commit", "-q", "-m", "batch", when=T0 + timedelta(minutes=20))
    out = status_at(capsys, m, clock, 50)
    assert "minutes since last commit or journal line: 30" in out
    assert STALLED not in out
    assert STALLED in status_at(capsys, m, clock, 51)


def test_status_counts_merged_batches_and_new_matches(repo, capsys):
    m, clock, _ = started(repo, capsys)
    git(repo, "switch", "-q", "-c", "batch-1")
    functions(repo, 7, 2)
    git(repo, "commit", "-q", "-am", "match", when=T0 + timedelta(minutes=5))
    git(repo, "switch", "-q", "match/night-2026-11-25")
    git(
        repo,
        "merge",
        "-q",
        "--no-ff",
        "-m",
        "merge",
        "batch-1",
        when=T0 + timedelta(minutes=6),
    )
    out = status_at(capsys, m, clock, 10)
    assert "batches merged: 1" in out
    assert "since start: 4 matched, 1 parked" in out
    assert "minutes since last commit or journal line: 4" in out
    assert "ghidra-mcp: up" in out


def test_status_appends_one_row_per_call_to_the_log(repo, capsys):
    m, clock, _ = started(repo, capsys)
    status_at(capsys, m, clock, 60)
    rows = (repo / "build/overnight/log.tsv").read_text().splitlines()
    assert rows[0].split("\t") == list(overnight.LOG_HEADER)
    assert len(rows) == 3
    assert rows[2].split("\t")[1:3] == ["60", "420"]


def test_status_without_a_run_says_so(repo, capsys):
    code, out = run_cli(capsys, machine(repo, Clock(T0), Fakes(repo)), "status")
    assert code == 1
    assert "no run" in out


@pytest.fixture
def ready(repo, monkeypatch):
    """A checkout where every preflight check passes."""
    (repo / "orig").mkdir()
    (repo / "orig/default.xbe").write_bytes(XBE_BYTES)
    monkeypatch.setattr(
        overnight, "EXPECTED_XBE_SHA256", hashlib.sha256(XBE_BYTES).hexdigest()
    )
    for path in overnight.INPUTS:
        (repo / path).mkdir(parents=True, exist_ok=True)
    (repo / "ghidra").mkdir()
    symbols = [Entry(0x11000, "function", 20, "CreateThread", "sdk", "xbe-loader")]
    write_symbols(repo / "config/symbols.txt", symbols)
    write_stamp(repo / "config/symbols.txt", repo / "ghidra/.sync-stamp")
    (repo / ".gitignore").write_text("/build/\n/orig/\n/ghidra/\n/tools/\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "inputs", when=T0 - timedelta(days=1))
    git(repo, "push", "-q", "origin", "main")
    return repo


def test_preflight_passes_when_every_check_passes(ready, capsys):
    code, out = run_cli(capsys, machine(ready, Clock(T0), Fakes(ready)), "preflight")
    assert code == 0, out
    lines = out.splitlines()
    assert [line.split(":")[0] for line in lines[:-1]] == [
        n for n, _ in overnight.CHECKS
    ]
    assert all(line.endswith(": ok") for line in lines[:-1])
    assert lines[-1] == "preflight: pass"


def test_preflight_fails_on_an_uncommitted_change(ready, capsys):
    (ready / "config/functions.csv").write_text(HEADER)
    code, out = run_cli(capsys, machine(ready, Clock(T0), Fakes(ready)), "preflight")
    assert code == 1
    assert "uncommitted changes: fail (1 tracked files changed)" in out
    assert out.splitlines()[-1] == "preflight: fail"


def test_preflight_fails_on_an_assigned_ghidra_writer_task(ready, capsys):
    fakes = Fakes(ready)
    fakes.gh_issues = json.dumps(
        [
            {"number": 60, "title": "queued", "assignees": []},
            {"number": 61, "title": "rebuild", "assignees": [{"login": "someone"}]},
        ]
    )
    code, out = run_cli(capsys, machine(ready, Clock(T0), fakes), "preflight")
    assert code == 1
    assert "ghidra writer: fail (#61 rebuild (someone))" in out
    assert "#60" not in out


def test_preflight_fails_when_gh_fails(ready, capsys):
    fakes = Fakes(ready)
    fakes.answers[("gh", "auth", "status")] = (1, "", "not logged in")
    fakes.gh_issues = "gh: error"
    code, out = run_cli(capsys, machine(ready, Clock(T0), fakes), "preflight")
    assert code == 1
    assert "gh auth: fail" in out
    assert "ghidra writer: fail (gh issue list failed)" in out


def test_preflight_names_each_other_failing_check(ready, capsys):
    (ready / "orig/default.xbe").write_bytes(b"other")
    (ready / "build/strings.tsv").rmdir()
    (ready / "ghidra/.sync-stamp").unlink()
    fakes = Fakes(ready)
    fakes.answers[GATE[1]] = (1, "E501", "")
    m = machine(ready, Clock(T0), fakes, up=False)
    code, out = run_cli(capsys, m, "preflight")
    assert code == 1
    assert "xbe hash: fail (orig/default.xbe has SHA-256" in out
    assert "ignored inputs: fail (missing build/strings.tsv)" in out
    assert "ghidra project: fail (ghidra project: no sync stamp" in out
    assert "ghidra-mcp: fail" in out
    assert "gate: fail (uv run ruff check .)" in out


def test_finish_prints_gate_pass_only_when_every_command_passes(repo, capsys):
    m, clock, fakes = started(repo, capsys)
    clock.when = T0 + timedelta(hours=8)
    code, out = run_cli(capsys, m, "finish")
    assert code == 0
    assert out.splitlines()[0] == "gate: pass"
    assert "pull request: https://github.com/o/r/pull/1" in out
    assert ("gh", "pr", "ready", "match/night-2026-11-25") in fakes.calls
    for cmd in (*GATE, LEDGER_CHECK):
        assert cmd in fakes.calls
    run = json.loads((repo / "build/overnight/run.json").read_text())
    assert run["ended"] == "2026-11-26T06:00:00+00:00"
    assert run["gate"] == "pass"


@pytest.mark.parametrize("failing", [*GATE, LEDGER_CHECK])
def test_finish_names_the_failing_command(repo, capsys, failing):
    m, _, fakes = started(repo, capsys)
    fakes.answers[failing] = (1, "the reason\n", "")
    code, out = run_cli(capsys, m, "finish")
    assert code == 1
    assert "gate: pass" not in out
    assert f"gate: fail ({' '.join(failing)})" in out
    assert "the reason" in out
    assert not any(call[:3] == ("gh", "pr", "ready") for call in fakes.calls)
    run = json.loads((repo / "build/overnight/run.json").read_text())
    assert run["gate"] == "fail"
    assert run["ended"]


def test_finish_without_a_run_still_runs_the_gate(repo, capsys):
    fakes = Fakes(repo)
    fakes.answers[("gh", "pr", "view", "main", "--json", "url,headRefOid")] = (
        1,
        "",
        "no pull requests found",
    )
    code, out = run_cli(capsys, machine(repo, Clock(T0), fakes), "finish")
    assert code == 0
    assert "gate: pass" in out
    assert "pull request: none for main" in out
    assert not (repo / "build/overnight/run.json").exists()


def test_a_broken_run_file_is_no_run(tmp_path):
    path = tmp_path / "run.json"
    for text in (
        "",
        "garbage",
        "[]",
        '{"start": "x"}',
        '{"start": "2026-11-25"}',
        '{"start": "2026-11-25T22:00", "limit_minutes": 9, "branch": "b", "base": "c"}',
    ):
        path.write_text(text)
        assert overnight.read_run(path) is None


def test_preflight_fails_when_main_differs_from_origin_main(ready, capsys):
    (ready / "note.txt").write_text("x")
    git(ready, "add", "note.txt")
    git(ready, "commit", "-q", "-m", "local only")
    code, out = run_cli(capsys, machine(ready, Clock(T0), Fakes(ready)), "preflight")
    assert code == 1
    assert "main is origin/main: fail (main is " in out


def test_start_refuses_when_main_is_behind_origin_main(repo, tmp_path, capsys):
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(tmp_path / "origin.git"), str(other))
    (other / "merged.txt").write_text("x")
    git(other, "add", "merged.txt")
    git(other, "commit", "-q", "-m", "a night pull request")
    git(other, "push", "-q", "origin", "main")
    m = machine(repo, Clock(T0), Fakes(repo))
    code, out = run_cli(capsys, m, "start", "8h")
    assert code == 1
    assert "update main first; nothing changed" in out
    assert git(repo, "branch", "--show-current").strip() == "main"
    assert not (repo / "build/overnight/run.json").exists()


def test_start_refuses_a_dirty_checkout(repo, capsys):
    functions(repo, 1, 0)
    m = machine(repo, Clock(T0), Fakes(repo))
    code, out = run_cli(capsys, m, "start", "8h")
    assert code == 1
    assert "start: 1 tracked files changed; nothing changed" in out
    assert git(repo, "branch", "--show-current").strip() == "main"
    assert not (repo / "build/overnight/run.json").exists()


def test_start_adds_a_suffix_when_the_run_branch_exists(repo, capsys):
    git(repo, "branch", "match/night-2026-11-25")
    git(repo, "branch", "match/night-2026-11-25-2")
    m = machine(repo, Clock(T0), Fakes(repo))
    code, out = run_cli(capsys, m, "start", "1h")
    assert code == 0
    assert "start: made run branch match/night-2026-11-25-3, limit 1h" in out
    assert git(repo, "branch", "--show-current").strip() == "match/night-2026-11-25-3"


def test_a_journal_line_counts_as_activity(repo, capsys):
    m, clock, _ = started(repo, capsys)
    journal = repo / "build/overnight/journal.md"
    journal.write_text("batch 1: gate failed, reset\n")
    when = (T0 + timedelta(minutes=25)).timestamp()
    os.utime(journal, (when, when))
    out = status_at(capsys, m, clock, 55)
    assert "minutes since last commit or journal line: 30" in out
    assert STALLED not in out
    assert STALLED in status_at(capsys, m, clock, 56)


def test_status_of_an_ended_run_is_frozen_and_logs_nothing(repo, capsys):
    m, clock, _ = started(repo, capsys)
    clock.when = T0 + timedelta(minutes=470)
    assert run_cli(capsys, m, "finish")[0] == 0
    log = (repo / "build/overnight/log.tsv").read_text()
    out = status_at(capsys, m, clock, 900)
    assert "elapsed: 7h50m of 8h" in out
    assert "run: ended 2026-11-26T05:50:00+00:00" in out
    assert "wrap up" not in out
    assert STALLED not in out
    assert (repo / "build/overnight/log.tsv").read_text() == log


@pytest.mark.parametrize("command", [("start", "8h"), ("status",)])
def test_an_unreadable_run_file_gives_the_recovery_steps(repo, capsys, command):
    (repo / "build/overnight").mkdir(parents=True)
    (repo / "build/overnight/run.json").write_text("garbage")
    code, out = run_cli(capsys, machine(repo, Clock(T0), Fakes(repo)), *command)
    assert code == 1
    assert "cannot be read; to start a new run:" in out


def test_finish_fails_on_another_branch_and_does_not_mark_ready(repo, capsys):
    m, _, fakes = started(repo, capsys)
    git(repo, "switch", "-q", "main")
    code, out = run_cli(capsys, m, "finish")
    assert code == 1
    assert "gate: fail (the checkout is on main, not on match/night-2026-11-25)" in out
    assert not any(call in fakes.calls for call in (*GATE, LEDGER_CHECK))
    assert not any(call[:3] == ("gh", "pr", "ready") for call in fakes.calls)


def test_finish_fails_when_head_is_not_the_pull_request_head(repo, capsys):
    m, _, fakes = started(repo, capsys)
    fakes.pr_head = "0" * 40
    code, out = run_cli(capsys, m, "finish")
    assert code == 1
    assert f"is not the pull request head {'0' * 40}" in out
    assert "gate: pass" not in out
    assert not any(call[:3] == ("gh", "pr", "ready") for call in fakes.calls)
    run = json.loads((repo / "build/overnight/run.json").read_text())
    assert run["gate"] == "fail"


def test_shell_keeps_stdout_and_stderr_apart_and_times_out(tmp_path, monkeypatch):
    run = overnight.shell(tmp_path)
    assert run(["sh", "-c", "echo out; echo err >&2"]) == (0, "out\n", "err\n")
    monkeypatch.setattr(overnight, "CALL_TIMEOUT", 0.2)
    code, out, err = run(["sleep", "5"])
    assert (code, out) == (124, "")
    assert "timed out" in err


def test_a_url_with_no_scheme_is_no_answer():
    assert overnight.answers("127.0.0.1:1") is False
