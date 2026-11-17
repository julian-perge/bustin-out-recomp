import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

LINK_CHECKED_DOCS = [
    "CODING_STANDARDS.md",
    "docs/METHODOLOGY.md",
    "CONTRIBUTING.md",
    "docs/SUBSYSTEMS.md",
    "docs/ARCHITECTURE.md",
    "docs/CODE_MAP.md",
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


def test_each_issue_form_sets_the_needs_triage_label():
    forms = [
        form
        for form in sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
        if form.name != "config.yml"
    ]
    assert forms != []
    unlabeled = [
        form.name
        for form in forms
        if not re.search(
            r"^labels:\s*(\[[^\]]*\bneeds-triage\b[^\]]*\]|\n\s+- needs-triage\s*$)",
            form.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    ]
    assert unlabeled == []


def milestone_rows(name):
    text = read(name)
    table = text.split("## Milestones", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\| (M\d+ [^|]*?) \|", table, re.MULTILINE)


def test_status_and_methodology_list_the_same_milestones():
    status = milestone_rows("docs/STATUS.md")
    assert status != []
    assert status == milestone_rows("docs/METHODOLOGY.md")


def subsystem_file_lines():
    return re.findall(r"^- Files: (.*)$", read("docs/SUBSYSTEMS.md"), re.MULTILINE)


def test_each_module_and_script_is_in_exactly_one_subsystem():
    owned = [
        path
        for line in subsystem_file_lines()
        for path in re.findall(r"`([^`]+)`", line)
    ]
    expected = sorted(
        name
        for name in tracked_files()
        if (
            name.startswith("bodecomp/")
            and name.endswith(".py")
            and name != "bodecomp/__init__.py"
        )
        or (name.startswith("tools/") and name.count("/") == 1)
        or name.startswith("tools/ghidra_scripts/")
    )
    missing = [name for name in expected if name not in owned]
    repeated = sorted({name for name in owned if owned.count(name) > 1})
    assert (missing, repeated) == ([], [])


def is_tracked_path(path, tracked):
    if path in tracked:
        return True
    prefix = path.rstrip("/") + "/"
    return any(name.startswith(prefix) for name in tracked)


def repo_path(doc, target):
    parts = []
    for part in (PurePosixPath(doc).parent / target.split("#", 1)[0]).parts:
        if part == "..":
            if not parts:
                return None
            parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


def test_repo_path_resolves_relative_links():
    assert repo_path("docs/CODE_MAP.md", "../AGENTS.md#commands") == "AGENTS.md"
    assert repo_path("docs/CODE_MAP.md", "./adr/") == "docs/adr"
    assert repo_path("CONTRIBUTING.md", "../outside.md") is None


def broken_links(doc, tracked):
    broken = []
    for target in MARKDOWN_LINK.findall(read(doc)):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        path = repo_path(doc, target)
        if path is None or not is_tracked_path(path, tracked):
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
