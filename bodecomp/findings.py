from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

FINDINGS = Path("docs/FINDINGS.md")
# The public repo starts from one fresh commit (ADR-0016). Entries that were
# fixed before it cite commits of the old private history, and this file lists
# the hashes of that history.
PRE_PUBLIC = Path("config/pre-public-commits.txt")
HEADING = re.compile(r"^## (F-\d{4}) (\S.*)$")
# A heading that only looks like a finding is an error rather than plain text,
# because a skipped entry would vanish from the SessionStart summary.
NEAR_HEADING = re.compile(r"^\s*#+\s*[Ff]-\d")
STATUS = re.compile(
    r"^- Status: (?:(?P<plain>open|confirmed|rejected)"
    r"|active \((?P<owner>[^,()]+), (?P<date>\d{4}-\d{2}-\d{2})\)"
    r"|fixed \((?P<commit>[0-9a-f]{7,40})\))$"
)
MORE = "rg -n 'Status: (open|active)' docs/FINDINGS.md"


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    status: str
    line: int
    owner: str | None = None
    date: str | None = None
    commit: str | None = None


def parse(text: str) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    errors: list[str] = []
    current: tuple[str, str, int] | None = None
    has_status = False

    def close() -> None:
        if current and not has_status:
            errors.append(f"line {current[2]}: {current[0]} has no Status line")

    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if line.startswith("## ") or NEAR_HEADING.match(line):
            close()
            match = HEADING.match(line)
            if match:
                current, has_status = (match[1], match[2], number), False
            else:
                errors.append(
                    f"line {number}: every '## ' heading must be "
                    f"'## F-NNNN <title>': {line}"
                )
                current = None
            continue
        if current and line.startswith("- Status:"):
            if has_status:
                errors.append(f"line {number}: {current[0]} has a second Status line")
                continue
            has_status = True
            match = STATUS.match(line)
            if not match:
                value = line.removeprefix("- Status:").strip()
                errors.append(
                    f"line {number}: {current[0]} has an invalid status: {value}"
                )
                continue
            status = match["plain"] or ("active" if match["owner"] else "fixed")
            findings.append(
                Finding(
                    current[0],
                    current[1],
                    status,
                    current[2],
                    match["owner"],
                    match["date"],
                    match["commit"],
                )
            )
    close()
    return findings, errors


def commit_exists(sha: str, repo: Path = Path(".")) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
    )
    return result.returncode == 0


def pre_public_commits(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def commit_known(sha: str, repo: Path, pre_public: list[str]) -> bool:
    return any(full.startswith(sha) for full in pre_public) or commit_exists(sha, repo)


def check(findings: list[Finding], commit_exists: Callable[[str], bool]) -> list[str]:
    errors = []
    seen: set[str] = set()
    for f in findings:
        if f.id in seen:
            errors.append(f"line {f.line}: {f.id} is used twice")
        seen.add(f.id)
        if f.commit and not commit_exists(f.commit):
            errors.append(
                f"line {f.line}: {f.id} names commit {f.commit}, which does not exist"
            )
    return errors


def summary(findings: list[Finding], limit: int) -> list[str]:
    live = sorted(
        (f for f in findings if f.status in ("open", "active")), key=lambda f: f.id
    )
    lines = []
    for f in live[:limit]:
        state = f"active ({f.owner}, {f.date})" if f.status == "active" else "open"
        lines.append(f"{f.id} {state}: {f.title}")
    if len(live) > limit:
        lines.append(f"... and {len(live) - limit} more: {MORE}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.findings")
    parser.add_argument("command", choices=("check", "summary"))
    parser.add_argument("--path", type=Path, default=FINDINGS)
    parser.add_argument("--pre-public", type=Path, default=PRE_PUBLIC)
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args(argv)
    findings, errors = parse(args.path.read_text())
    if args.command == "summary":
        print("\n".join(summary(findings, args.limit)) or "(none)")
        if errors:
            print(
                f"({len(errors)} format problems: "
                "run python -m bodecomp.findings check)"
            )
        return 0
    repo = args.path.resolve().parent
    pre_public = pre_public_commits(args.pre_public)
    errors += check(findings, lambda sha: commit_known(sha, repo, pre_public))
    for error in errors:
        print(f"{args.path}: {error}", file=sys.stderr)
    if not errors:
        print(f"{args.path}: {len(findings)} findings, no problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
