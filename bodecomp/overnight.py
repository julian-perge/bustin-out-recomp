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
JOURNAL = STATE / "journal.md"
XBE = Path("orig/default.xbe")
INPUTS = (
    Path("build/target"),
    Path("build/strings.tsv"),
    Path("tools/wibo"),
    Path("tools/xdk"),
)
URL = os.environ.get("GHIDRA_MCP_URL", "http://127.0.0.1:8089")
# The second night run (#97) took about 9.6 minutes per batch and at most about
# 16, so 30 minutes with no commit and no journal line means a stall. Row 6 of
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
# git and gh calls get this many seconds. The gate commands get no limit.
CALL_TIMEOUT = 60
NEW_RUN = (
    "only the user starts a new run, and the lead does none of these steps: "
    "the user copies what is needed from build/overnight/journal.md, "
    "removes the night worktrees with git worktree remove, deletes build/overnight/, "
    "then runs uv run python -m bodecomp.overnight preflight and start again"
)
STALLED = (
    "stalled: stop the running matcher, park its open functions, start the next batch"
)

# A runner returns the exit code, the standard output and the error output.
Runner = Callable[[Sequence[str]], tuple[int, str, str]]


def shell(root: Path) -> Runner:
    def run(cmd: Sequence[str]) -> tuple[int, str, str]:
        timeout = None if tuple(cmd) in (*GATE, LEDGER_CHECK) else CALL_TIMEOUT
        # Nobody answers a credential prompt in a run, so git fails at once.
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        try:
            done = subprocess.run(
                list(cmd),
                cwd=root,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return 124, "", f"timed out after {timeout} seconds"
        except OSError as error:
            return 127, "", str(error)
        return done.returncode, done.stdout, done.stderr

    return run


def answers(url: str = URL, timeout: float = 2) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/check_connection", timeout=timeout):
            return True
    except (OSError, ValueError):
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
        if datetime.fromisoformat(data["start"]).tzinfo is None:
            return None
        int(data["limit_minutes"])
        str(data["branch"])
        str(data["base"])
        if data.get("ended"):
            datetime.fromisoformat(data["ended"])
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
    code, out, _ = m.run(
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
    code, out, _ = m.run(["git", "log", "-1", "--format=%ct", branch])
    if code != 0 or not out.strip().isdigit():
        return None
    return datetime.fromtimestamp(int(out.strip()), UTC)


def journal_time(m: Machine) -> datetime | None:
    try:
        return datetime.fromtimestamp((m.root / JOURNAL).stat().st_mtime, UTC)
    except OSError:
        return None


def git_out(m: Machine, *args: str) -> str | None:
    code, out, _ = m.run(["git", *args])
    return out.strip() if code == 0 else None


def other_worktrees(m: Machine) -> list[str]:
    code, out, _ = m.run(["git", "worktree", "list", "--porcelain"])
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
    live = is_live(run)
    now = m.now() if live else datetime.fromisoformat(run["ended"])
    start = datetime.fromisoformat(run["start"])
    limit = int(run["limit_minutes"])
    elapsed = minutes_between(start, now)
    remaining = max(0, limit - elapsed)
    batches = merged_batches(m, run)
    matched, parked = counts(m.root)
    matched -= int(run.get("matched_at_start", 0))
    parked -= int(run.get("parked_at_start", 0))
    # Before the first commit of the run, the last commit is the one on main,
    # which can be days old, so the idle time counts from the start at most. A
    # batch that failed the gate is reset and leaves no commit, but the lead
    # writes a journal line for it, so a journal line counts as activity too.
    times = [start, last_commit(m, run["branch"]), journal_time(m)]
    idle = minutes_between(max(t for t in times if t is not None), now)
    worktrees = other_worktrees(m)
    up = m.server_up()
    lines = [
        f"elapsed: {duration(elapsed)} of {duration(limit)}",
        f"remaining: {duration(remaining)}",
        f"branch: {run['branch']}",
        f"batches merged: {batches}",
        f"since start: {matched} matched, {parked} parked",
        f"minutes since last commit or journal line: {idle}",
        f"worktrees: {', '.join(worktrees) if worktrees else 'none'}",
        f"ghidra-mcp: {'up' if up else 'down'}",
    ]
    if not live:
        lines.append(f"run: ended {run['ended']}, gate: {run.get('gate', 'not run')}")
        return lines
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
        print(f"start: the run of {run['start']} has ended; {NEW_RUN}")
        return 1
    if path.exists():
        print(f"start: {RUN} cannot be read; {NEW_RUN}")
        return 1
    for check in (check_clean, check_origin_main):
        problem = check(m)
        if problem is not None:
            print(f"start: {problem}; nothing changed")
            return 1
    now = m.now()
    branch = free_branch(m, f"match/night-{now.date().isoformat()}")
    if branch is None:
        print("start: git ls-remote origin failed; nothing changed")
        return 1
    base = git_out(m, "rev-parse", "--verify", "main")
    code, _, err = m.run(["git", "switch", "-c", branch, "main"])
    if base is None or code != 0:
        print(f"start: could not make {branch} from main: {err.strip()}")
        return 1
    matched, parked = counts(m.root)
    run = {
        "start": now.isoformat(timespec="seconds"),
        "limit_minutes": limit,
        "branch": branch,
        "base": base,
        "matched_at_start": matched,
        "parked_at_start": parked,
        "ended": None,
    }
    write_run(path, run)
    print(f"start: made run branch {branch}, limit {duration(limit)}")
    print("\n".join(status(m, run)))
    return 0


def branch_exists(m: Machine, name: str) -> bool | None:
    """Say whether name is a branch here or on origin, or None when origin fails."""
    if git_out(m, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}"):
        return True
    # A branch can exist only on origin, such as a rehearsal pushed from another
    # clone. Its old pull request would then be found, and the push would fail.
    code, _, _ = m.run(["git", "ls-remote", "--exit-code", "--heads", "origin", name])
    if code == 2:
        return False
    return True if code == 0 else None


def free_branch(m: Machine, name: str) -> str | None:
    """Return name, or name with the first suffix -2, -3, ... that no branch has."""
    candidate, number = name, 1
    while (exists := branch_exists(m, candidate)) is not False:
        if exists is None:
            return None
        number += 1
        candidate = f"{name}-{number}"
    return candidate


def run_gate(m: Machine, commands: Sequence[Sequence[str]]) -> tuple[str, str] | None:
    """Return the first failing command and its output, or None."""
    for cmd in commands:
        code, out, err = m.run(cmd)
        if code != 0:
            return " ".join(cmd), out + err
    return None


def tail(text: str, count: int = 20) -> str:
    return "\n".join(text.rstrip().splitlines()[-count:])


def check_clean(m: Machine) -> str | None:
    out = git_out(m, "status", "--porcelain", "--untracked-files=no")
    if out is None:
        return "git status failed"
    changed = out.splitlines()
    return f"{len(changed)} tracked files changed" if changed else None


def check_origin_main(m: Machine) -> str | None:
    # start makes the run branch from local main, and the user merges each night
    # pull request on GitHub, so local main can be behind origin/main.
    code, _, err = m.run(["git", "fetch", "origin", "main"])
    if code != 0:
        return f"git fetch origin main failed: {err.strip()}"
    local = git_out(m, "rev-parse", "--verify", "main")
    remote = git_out(m, "rev-parse", "--verify", "origin/main")
    if local is None or remote is None:
        return "main or origin/main is missing"
    if local == remote:
        return None
    if m.run(["git", "merge-base", "--is-ancestor", "main", "origin/main"])[0] == 0:
        return f"main {local} is behind origin/main {remote}; update main first"
    if m.run(["git", "merge-base", "--is-ancestor", "origin/main", "main"])[0] == 0:
        return (
            f"main {local} is ahead of origin/main {remote}; "
            "the user pushes main or resets it to origin/main"
        )
    return f"main {local} and origin/main {remote} differ; the user resolves this"


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
    code, _, _ = m.run(["gh", "auth", "status"])
    return None if code == 0 else "gh auth status failed"


def check_ghidra_writer(m: Machine) -> str | None:
    code, out, _ = m.run(
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
    ("main is origin/main", check_origin_main),
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


def pull_request(m: Machine, branch: str) -> tuple[str, str] | None:
    """Return the URL and the head commit of the branch's pull request, or None."""
    code, out, _ = m.run(["gh", "pr", "view", branch, "--json", "url,headRefOid"])
    try:
        found = json.loads(out) if code == 0 else None
        return str(found["url"]), str(found["headRefOid"])
    except (ValueError, TypeError, KeyError):
        return None


def finish(m: Machine) -> int:
    path = m.root / RUN
    run = read_run(path)
    current = git_out(m, "branch", "--show-current") or ""
    head = git_out(m, "rev-parse", "HEAD")
    branch = run["branch"] if run is not None else current
    pr = pull_request(m, branch)
    # The gate proves only the code it ran on, so finish runs it only on the
    # commit that the pull request holds.
    changed = git_out(m, "status", "--porcelain")
    mismatch = None
    if run is not None and current != branch:
        mismatch = f"the checkout is on {current or 'no branch'}, not on {branch}"
    elif changed is None or changed:
        count = "some" if changed is None else len(changed.splitlines())
        mismatch = f"{count} files are changed or untracked; commit or remove them"
    elif pr is not None and pr[1] != head:
        mismatch = f"HEAD {head} is not the pull request head {pr[1]}; push {branch}"
    failed = None if mismatch else run_gate(m, [*GATE, LEDGER_CHECK])
    passed = mismatch is None and failed is None
    if mismatch:
        print(f"gate: fail ({mismatch})")
    elif failed:
        print(f"gate: fail ({failed[0]})")
        print(tail(failed[1]))
    else:
        print("gate: pass")
    if pr is None:
        print(f"pull request: none for {branch}")
    else:
        if passed and m.run(["gh", "pr", "ready", branch])[0] != 0:
            print("pull request: could not mark it ready")
        print(f"pull request: {pr[0]}")
    if run is not None:
        run["ended"] = run.get("ended") or m.now().isoformat(timespec="seconds")
        run["gate"] = "pass" if passed else "fail"
        write_run(path, run)
        print(f"run: ended {run['ended']}")
    return 0 if passed else 1


def hook_line(m: Machine) -> str | None:
    """Return the line that tools/session-start.sh prints for a live run."""
    run = read_run(m.root / RUN)
    if not is_live(run):
        return None
    elapsed = minutes_between(datetime.fromisoformat(run["start"]), m.now())
    return (
        f"overnight run: {duration(elapsed)} of {duration(int(run['limit_minutes']))}, "
        f"branch {run['branch']}, {merged_batches(m, run)} batches merged; "
        'run "uv run python -m bodecomp.overnight status", '
        "rules in docs/WORKFLOW.md (An unattended run)"
    )


def main(argv: list[str] | None = None, machine: Machine | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.overnight")
    parser.add_argument("--root", type=Path, default=Path())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight", help="check that a run can start")
    begin = sub.add_parser("start", help="start a run, or show the live one")
    begin.add_argument("limit", type=parse_duration, help="such as 8h or 90m")
    sub.add_parser("status", help="print the clock and the progress of the run")
    sub.add_parser("finish", help="run the gate and end the run")
    sub.add_parser("hook-line", help="the session hook's line for a live run")
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
    if args.command == "hook-line":
        line = hook_line(m)
        if line:
            print(line)
        return 0
    path = m.root / RUN
    run = read_run(path)
    if run is None and path.exists():
        print(f"status: {RUN} cannot be read; {NEW_RUN}")
        return 1
    if run is None:
        print("status: no run; start one with")
        print("  uv run python -m bodecomp.overnight start 8h")
        return 1
    print("\n".join(status(m, run)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
