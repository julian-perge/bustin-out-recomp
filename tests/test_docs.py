import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

LINK_CHECKED_DOCS = [
    "CODING_STANDARDS.md",
]

MARKDOWN_LINK = re.compile(r"\]\(([^)\s]+)\)")
RULE_HEADING = re.compile(r"^## (S\d+) ", re.MULTILINE)


def tracked_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return set(out.splitlines())


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def rule_ids():
    return RULE_HEADING.findall(read("CODING_STANDARDS.md"))


def test_coding_standards_state_rules_s1_to_s4():
    assert rule_ids() == ["S1", "S2", "S3", "S4"]


def test_reviewer_agent_checks_each_rule():
    text = read(".claude/agents/reviewer.md")
    missing = [rule for rule in rule_ids() if not re.search(rf"\b{rule}\b", text)]
    assert missing == []


def test_pull_request_template_has_a_section_per_rule():
    text = read(".github/pull_request_template.md")
    missing = [
        rule
        for rule in rule_ids()
        if not re.search(rf"^#+ {rule}\b", text, re.MULTILINE)
    ]
    assert missing == []


def is_tracked_path(path, tracked):
    if path in tracked:
        return True
    prefix = path.rstrip("/") + "/"
    return any(name.startswith(prefix) for name in tracked)


def broken_links(doc, tracked):
    broken = []
    base = PurePosixPath(doc).parent
    for target in MARKDOWN_LINK.findall(read(doc)):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        path = target.split("#", 1)[0]
        parts = []
        for part in (base / path).parts:
            if part == "..":
                parts.pop()
            elif part != ".":
                parts.append(part)
        if not is_tracked_path("/".join(parts), tracked):
            broken.append(f"{doc}: {target}")
    return broken


def test_relative_links_in_the_checked_docs_point_to_tracked_paths():
    tracked = tracked_files()
    broken = [link for doc in LINK_CHECKED_DOCS for link in broken_links(doc, tracked)]
    assert broken == []


def test_agents_md_has_at_most_100_lines():
    assert len(read("AGENTS.md").splitlines()) <= 100


def test_tracked_markdown_files_are_ascii():
    not_ascii = []
    for name in sorted(tracked_files()):
        path = ROOT / name
        if name.endswith(".md") and path.is_file() and not path.read_bytes().isascii():
            not_ascii.append(name)
    assert not_ascii == []
