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


REMOVED_MARKERS = ("active:" + "start", "active:" + "end")
MARKER_EXEMPT = ("spec/",)


def test_no_tracked_file_names_the_removed_active_block_markers():
    # The spec of issue #56 names the markers, so spec/ is exempt.
    found = []
    for name in sorted(tracked_files()):
        if name.startswith(MARKER_EXEMPT) or not (ROOT / name).is_file():
            continue
        try:
            text = read(name)
        except UnicodeDecodeError:
            continue
        found += [f"{name}: {m}" for m in REMOVED_MARKERS if m in text]
    assert found == []


ACTIVE_BLOCK_EXEMPT = ("docs/adr/", "spec/")


def test_no_doc_names_the_removed_active_block():
    # ADRs, the milestone results and the spec name the block as it was.
    found = []
    for name in sorted(tracked_files()):
        if name.startswith(ACTIVE_BLOCK_EXEMPT) or not (ROOT / name).is_file():
            continue
        if re.fullmatch(r"docs/m\d+-results\.md", name):
            continue
        if not name.endswith(".md"):
            continue
        if "Active block" in read(name):
            found.append(name)
    assert found == []


def section(text, heading):
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, heading
    return match.group(1)


def test_namer_and_reviewer_read_the_ghidra_writer_label():
    for name in ("namer", "reviewer"):
        text = read(f".claude/agents/{name}.md")
        assert "gh issue list --label ghidra-writer" in text, name
        assert "Ghidra writer' docs/STATUS.md" not in text, name


def test_matcher_reads_the_hook_output():
    text = read(".claude/agents/matcher.md")
    assert "Read the hook output." in text
    assert "Read the Active block" not in text


def test_end_of_a_batch_does_not_replace_a_status_block():
    for name in ("AGENTS.md", "docs/WORKFLOW.md"):
        assert "STATUS.md" not in section(read(name), "End of a batch"), name


def test_plan_stage_puts_the_ghidra_writer_label_on_tasks():
    text = section(read("docs/agents/workflow.md"), "Plan")
    assert "`ghidra-writer`" in text
    assert "The assignee is the lock." in text


def test_workflow_says_other_ghidra_changes_are_scratch():
    text = read("docs/WORKFLOW.md")
    assert "is scratch" in text
    assert "ADR-0021" in text


def matcher_bullet(finding):
    text = read(".claude/agents/matcher.md")
    lines = [line for line in text.splitlines() if f"({finding})" in line]
    assert len(lines) == 1, finding
    return lines[0]


def test_matcher_names_the_declared_and_generated_lines():
    line = matcher_bullet("F-0098")
    assert "`// declared: 0x" in line
    assert "S_000A80B0::FUN_00124940" in line
    assert "`// generated: 0x" in line
    assert '`docs/WORKFLOW.md`, section "Matching"' in line


def test_matcher_blurs_register_names_before_a_register_tie_park():
    line = matcher_bullet("F-0092")
    assert "`register tie`" in line
    assert "register names blurred" in line


def test_matcher_looks_for_the_same_statements_before_a_scheduling_park():
    line = matcher_bullet("F-0094")
    assert "`scheduling`" in line
    assert "inline helper of a base class" in line
    assert "look in Ghidra" in line


def test_matcher_defines_a_callee_in_place_of_throw():
    line = matcher_bullet("F-0095")
    assert "`throw()`" in line
    assert "define the callee in the same source" in line
    assert "Give the callee its address comment" in line


def bullets_with(path, findings):
    text = read(path)
    return [line for line in text.splitlines() if f"({findings})" in line]


def test_matcher_compiles_the_donor_form_before_a_park():
    lines = bullets_with(".claude/agents/matcher.md", "F-0093, F-0101")
    assert len(lines) == 1
    line = lines[0]
    assert "GameCube donor" in line
    assert "compile the donor's form of the function" in line
    assert "before you park it" in line


def test_reviewer_fails_a_park_without_the_donor_form():
    text = read(".claude/agents/reviewer.md")
    s2 = text.split("S2 Evidence for claims", 1)[1].split("S3 Evidence for names", 1)[0]
    lines = [line for line in s2.splitlines() if "(F-0093, F-0101)" in line]
    assert len(lines) == 1
    line = lines[0]
    assert "GameCube donor" in line
    assert "donor's form" in line
    assert "is a fail" in line
