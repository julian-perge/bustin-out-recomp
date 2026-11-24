from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from bodecomp.match import FUNCTIONS, read_functions
from bodecomp.setup_inputs import EXPECTED_XBE_SHA256
from bodecomp.sync import STAMP, SYMBOLS, freshness

STATE = Path("build/overnight")
RUN = STATE / "run.json"
LOG = STATE / "log.tsv"
XBE = Path("orig/default.xbe")
INPUTS = (
    Path("build/target"),
    Path("build/strings.tsv"),
    Path("tools/wibo"),
    Path("tools/xdk"),
)
URL = os.environ.get("GHIDRA_MCP_URL", "http://127.0.0.1:8089")
# The second night run (#97) took about 9.6 minutes per batch and at most about
# 16, so 30 minutes with no commit means a stall. Row 6 of
# docs/research/10-overnight-design.md sets the final value after the rehearsal.
STALL_MINUTES = 30
WRAP_UP_PERCENT = 85
# The gate of AGENTS.md ("Every task"), in its order, one command at a time.
GATE = (
    ("uv", "run", "pytest", "-q"),
    ("uv", "run", "ruff", "check", "."),
    ("uv", "run", "python", "-m", "bodecomp.findings", "check"),
    ("uv", "run", "python", "-m", "bodecomp.match", "--check"),
)
LEDGER_CHECK = ("uv", "run", "python", "-m", "bodecomp.ledger", "--check")
LOG_HEADER = (
    "time",
    "elapsed_min",
    "remaining_min",
    "batches",
    "matched",
    "parked",
    "idle_min",
    "worktrees",
    "server",
)
STALLED = (
    "stalled: stop the running matcher, park its open functions, start the next batch"
)

Runner = Callable[[Sequence[str]], tuple[int, str]]


def shell(root: Path) -> Runner:
    def run(cmd: Sequence[str]) -> tuple[int, str]:
        try:
            done = subprocess.run(list(cmd), cwd=root, capture_output=True, text=True)
        except OSError as error:
            return 127, str(error)
        return done.returncode, done.stdout + done.stderr

    return run


def answers(url: str = URL, timeout: float = 2) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/check_connection", timeout=timeout):
            return True
    except OSError:
        return False


@dataclass
class Machine:
    root: Path
    run: Runner
    now: Callable[[], datetime]
    server_up: Callable[[], bool]


def parse_duration(text: str) -> int:
    match = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?", text)
    minutes = 0
    if match and any(match.groups()):
        minutes = int(match.group(1) or 0) * 60 + int(match.group(2) or 0)
    if minutes <= 0:
        raise argparse.ArgumentTypeError(f"not a duration such as 8h or 90m: {text}")
    return minutes


def duration(minutes: int) -> str:
    hours, rest = divmod(max(0, minutes), 60)
    if hours and rest:
        return f"{hours}h{rest}m"
    return f"{hours}h" if hours else f"{rest}m"


def read_run(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
        datetime.fromisoformat(data["start"])
        int(data["limit_minutes"])
        str(data["branch"])
        str(data["base"])
    except (OSError, ValueError, TypeError, KeyError):
        return None
    return data


def is_live(run: dict | None) -> bool:
    return run is not None and not run.get("ended")


def write_run(path: Path, run: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run, indent=2) + "\n")


def counts(root: Path) -> tuple[int, int]:
    statuses = [status for status, _ in read_functions(root / FUNCTIONS).values()]
    return statuses.count("matched"), statuses.count("parked")


def minutes_between(earlier: datetime, later: datetime) -> int:
    return max(0, int((later - earlier).total_seconds() // 60))


def merged_batches(m: Machine, run: dict) -> int:
    code, out = m.run(
        [
            "git",
            "rev-list",
            "--count",
            "--merges",
            "--first-parent",
            f"{run['base']}..{run['branch']}",
        ]
    )
    return int(out.strip()) if code == 0 and out.strip().isdigit() else 0


def last_commit(m: Machine, branch: str) -> datetime | None:
    code, out = m.run(["git", "log", "-1", "--format=%ct", branch])
    if code != 0 or not out.strip().isdigit():
        return None
    return datetime.fromtimestamp(int(out.strip()), UTC)


def other_worktrees(m: Machine) -> list[str]:
    code, out = m.run(["git", "worktree", "list", "--porcelain"])
    if code != 0:
        return []
    here = m.root.resolve()
    paths = [
        line.removeprefix("worktree ")
        for line in out.splitlines()
        if line.startswith("worktree ")
    ]
    return [p for p in paths if Path(p).resolve() != here]


def status(m: Machine, run: dict) -> list[str]:
    now = m.now()
    start = datetime.fromisoformat(run["start"])
    limit = int(run["limit_minutes"])
    elapsed = minutes_between(start, now)
    remaining = max(0, limit - elapsed)
    batches = merged_batches(m, run)
    matched, parked = counts(m.root)
    matched -= int(run.get("matched_at_start", 0))
    parked -= int(run.get("parked_at_start", 0))
    # Before the first commit of the run, the last commit is the one on main,
    # which can be days old, so the idle time counts from the start at most.
    last = last_commit(m, run["branch"])
    idle = minutes_between(start if last is None else max(start, last), now)
    worktrees = other_worktrees(m)
    up = m.server_up()
    lines = [
        f"elapsed: {duration(elapsed)} of {duration(limit)}",
        f"remaining: {duration(remaining)}",
        f"branch: {run['branch']}",
        f"batches merged: {batches}",
        f"since start: {matched} matched, {parked} parked",
        f"minutes since last commit: {idle}",
        f"worktrees: {', '.join(worktrees) if worktrees else 'none'}",
        f"ghidra-mcp: {'up' if up else 'down'}",
    ]
    if elapsed * 100 >= limit * WRAP_UP_PERCENT:
        lines.append("wrap up: start no new batch")
    if idle > STALL_MINUTES:
        lines.append(STALLED)
    row = (
        now.isoformat(timespec="seconds"),
        elapsed,
        remaining,
        batches,
        matched,
        parked,
        idle,
        len(worktrees),
        "up" if up else "down",
    )
    log = m.root / LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        if log.stat().st_size == 0:
            f.write("\t".join(LOG_HEADER) + "\n")
        f.write("\t".join(str(x) for x in row) + "\n")
    return lines


def start(m: Machine, limit: int) -> int:
    path = m.root / RUN
    run = read_run(path)
    if is_live(run):
        print("start: a run is live, nothing changed")
        print("\n".join(status(m, run)))
        return 0
    if run is not None:
        print(f"start: the run of {run['start']} has ended; delete {STATE} first")
        return 1
    if path.exists():
        print(f"start: {RUN} cannot be read; delete it first")
        return 1
    now = m.now()
    branch = f"match/night-{now.date().isoformat()}"
    code, base = m.run(["git", "rev-parse", "--verify", "main"])
    if code != 0:
        print(f"start: no main branch: {base.strip()}")
        return 1
    code, out = m.run(["git", "switch", "-c", branch, "main"])
    if code != 0:
        print(f"start: could not make {branch}: {out.strip()}")
        return 1
    matched, parked = counts(m.root)
    run = {
        "start": now.isoformat(timespec="seconds"),
        "limit_minutes": limit,
        "branch": branch,
        "base": base.strip(),
        "matched_at_start": matched,
        "parked_at_start": parked,
        "ended": None,
    }
    write_run(path, run)
    print(f"start: run branch {branch}, limit {duration(limit)}")
    print("\n".join(status(m, run)))
    return 0


def run_gate(m: Machine, commands: Sequence[Sequence[str]]) -> tuple[str, str] | None:
    """Return the first failing command and its output, or None."""
    for cmd in commands:
        code, out = m.run(cmd)
        if code != 0:
            return " ".join(cmd), out
    return None


def tail(text: str, count: int = 20) -> str:
    return "\n".join(text.rstrip().splitlines()[-count:])


def check_clean(m: Machine) -> str | None:
    code, out = m.run(["git", "status", "--porcelain", "--untracked-files=no"])
    if code != 0:
        return "git status failed"
    changed = out.splitlines()
    return f"{len(changed)} tracked files changed" if changed else None


def check_xbe(m: Machine) -> str | None:
    path = m.root / XBE
    if not path.is_file():
        return f"{XBE} is missing"
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != EXPECTED_XBE_SHA256:
        return f"{XBE} has SHA-256 {digest.hexdigest()}"
    return None


def check_inputs(m: Machine) -> str | None:
    missing = [str(p) for p in INPUTS if not (m.root / p).exists()]
    return f"missing {', '.join(missing)}" if missing else None


def check_ghidra_project(m: Machine) -> str | None:
    line = freshness(m.root / SYMBOLS, m.root / STAMP)
    return None if line.startswith("ghidra project: level") else line


def check_server(m: Machine) -> str | None:
    return None if m.server_up() else f"no answer from {URL}/check_connection"


def check_gh_auth(m: Machine) -> str | None:
    code, _ = m.run(["gh", "auth", "status"])
    return None if code == 0 else "gh auth status failed"


def check_ghidra_writer(m: Machine) -> str | None:
    code, out = m.run(
        [
            "gh",
            "issue",
            "list",
            "--label",
            "ghidra-writer",
            "--state",
            "open",
            "--json",
            "number,title,assignees",
        ]
    )
    try:
        issues = json.loads(out) if code == 0 else None
    except ValueError:
        issues = None
    if not isinstance(issues, list):
        return "gh issue list failed"
    assigned = [
        f"#{i['number']} {i['title']} ({', '.join(a['login'] for a in i['assignees'])})"
        for i in issues
        if i.get("assignees")
    ]
    return "; ".join(assigned) if assigned else None


def check_gate(m: Machine) -> str | None:
    failed = run_gate(m, GATE)
    return None if failed is None else failed[0]


CHECKS = (
    ("uncommitted changes", check_clean),
    ("xbe hash", check_xbe),
    ("ignored inputs", check_inputs),
    ("ghidra project", check_ghidra_project),
    ("ghidra-mcp", check_server),
    ("gh auth", check_gh_auth),
    ("ghidra writer", check_ghidra_writer),
    ("gate", check_gate),
)


def preflight(m: Machine) -> int:
    passed = True
    for name, check in CHECKS:
        problem = check(m)
        print(f"{name}: ok" if problem is None else f"{name}: fail ({problem})")
        passed = passed and problem is None
    print(f"preflight: {'pass' if passed else 'fail'}")
    return 0 if passed else 1


def finish(m: Machine) -> int:
    path = m.root / RUN
    run = read_run(path)
    failed = run_gate(m, [*GATE, LEDGER_CHECK])
    if failed is None:
        print("gate: pass")
    else:
        print(f"gate: fail ({failed[0]})")
        print(tail(failed[1]))
    if run is not None:
        branch = run["branch"]
    else:
        branch = m.run(["git", "branch", "--show-current"])[1].strip()
    code, url = m.run(["gh", "pr", "view", branch, "--json", "url", "--jq", ".url"])
    if code == 0 and url.strip():
        if failed is None and m.run(["gh", "pr", "ready", branch])[0] != 0:
            print("pull request: could not mark it ready")
        print(f"pull request: {url.strip()}")
    else:
        print(f"pull request: none for {branch}")
    if is_live(run):
        run["ended"] = m.now().isoformat(timespec="seconds")
        run["gate"] = "pass" if failed is None else "fail"
        write_run(path, run)
        print("run: ended")
    return 0 if failed is None else 1


def main(argv: list[str] | None = None, machine: Machine | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.overnight")
    parser.add_argument("--root", type=Path, default=Path())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight", help="check that a run can start")
    begin = sub.add_parser("start", help="start a run, or show the live one")
    begin.add_argument("limit", type=parse_duration, help="such as 8h or 90m")
    sub.add_parser("status", help="print the clock and the progress of the run")
    sub.add_parser("finish", help="run the gate and end the run")
    args = parser.parse_args(argv)
    m = machine or Machine(
        root=args.root,
        run=shell(args.root),
        now=lambda: datetime.now().astimezone(),
        server_up=answers,
    )
    if args.command == "preflight":
        return preflight(m)
    if args.command == "start":
        return start(m, args.limit)
    if args.command == "finish":
        return finish(m)
    run = read_run(m.root / RUN)
    if run is None:
        print("status: no run; start one with")
        print("  uv run python -m bodecomp.overnight start 8h")
        return 1
    print("\n".join(status(m, run)))
    if not is_live(run):
        print(f"run: ended {run['ended']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
