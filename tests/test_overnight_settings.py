import json
import re
from pathlib import Path

import pytest

from bodecomp.agent_tools import PREFIX, SNAPSHOT, read_only_tools, tool_name

ROOT = Path(__file__).resolve().parent.parent
OVERNIGHT = ROOT / "config/overnight-settings.json"
PROJECT = ROOT / ".claude/settings.json"
# The bridge registers these write tools itself, outside the server's schema
# (MANAGEMENT_TOOL_NAMES in ghidra-mcp's python/bridge_mcp_ghidra/config.py,
# without the read-only DISCOVERY tools of bodecomp/agent_tools.py).
BRIDGE_WRITE = (
    "connect_instance",
    "import_file",
    "load_tool_group",
    "unload_tool_group",
)
# The rules of R5 in docs/research/10-overnight-design.md.
ALLOW = [
    "Bash(uv run python -m bodecomp.*)",
    "Bash(uv run pytest *)",
    "Bash(uv run ruff check *)",
    "Bash(git worktree *)",
    "Bash(ln -s *)",
]
DENY = [
    "Bash(tools/rebuild-ghidra.sh*)",
    "Bash(tools/delink.sh*)",
    "Bash(tools/create-functions.sh*)",
    "Bash(gh pr merge*)",
    "Bash(git push --force*)",
    "Bash(git push -f*)",
    "Bash(git push * main)",
    "Bash(git push *:main)",
    "Bash(uv run python -m bodecomp.sync apply*)",
    "Bash(uv run python -m bodecomp.names set*)",
    "Bash(uv run python -m bodecomp.libmatch*)",
    # sync and names take options before the subcommand (sync.py, names.py), so
    # these rules match a subcommand after any options too.
    "Bash(uv run python -m bodecomp.sync *apply*)",
    "Bash(uv run python -m bodecomp.names *set*)",
    "Bash(git push *--force*)",
    "Bash(git push * -f*)",
    "Bash(git push *+main*)",
    "Bash(git push *refs/heads/main*)",
    # The links of "A matcher's worktree" name paths that differ per machine, so
    # the allow rule stays Bash(ln -s *) and a forced link is denied.
    "Bash(ln -s -f*)",
    "Bash(ln -sf*)",
    "Bash(ln -s --force*)",
]
SCHEMA = {
    "tools": [
        {"path": "/get_xrefs_to", "read_only": True},
        {"path": "/rename_function", "read_only": False},
        {"path": "/delete_function", "read_only": False},
    ]
}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def write_tools(schema: dict) -> list[str]:
    tools = {PREFIX + tool_name(tool["path"]) for tool in schema["tools"]}
    tools |= {PREFIX + name for name in BRIDGE_WRITE}
    return sorted(tools - set(read_only_tools(schema)))


def missing_denials(settings: dict, schema: dict) -> list[str]:
    deny = set(settings["permissions"]["deny"])
    return [tool for tool in write_tools(schema) if tool not in deny]


def test_the_file_holds_the_rules_of_r5():
    settings = load(OVERNIGHT)
    assert settings["env"] == {"CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "5"}
    assert settings["permissions"]["allow"] == ALLOW
    assert settings["permissions"]["deny"][: len(DENY)] == DENY
    rest = settings["permissions"]["deny"][len(DENY) :]
    assert rest == sorted(set(rest))
    assert all(rule.startswith(PREFIX) for rule in rest)


def test_no_allowed_rule_is_denied():
    deny = set(load(OVERNIGHT)["permissions"]["deny"])
    allowed = (
        load(OVERNIGHT)["permissions"]["allow"] + load(PROJECT)["permissions"]["allow"]
    )
    assert [rule for rule in allowed if rule in deny] == []


def test_a_write_tool_missing_from_the_deny_list_is_found():
    settings = {"permissions": {"deny": [PREFIX + "rename_function"]}}
    missing = missing_denials(settings, SCHEMA)
    assert PREFIX + "delete_function" in missing
    assert PREFIX + "load_tool_group" in missing
    assert PREFIX + "get_xrefs_to" not in missing
    assert PREFIX + "rename_function" not in missing


@pytest.mark.skipif(not SNAPSHOT.exists(), reason="no ghidra-mcp schema snapshot")
def test_every_ghidra_mcp_write_tool_is_denied():
    schema = json.loads(SNAPSHOT.read_text())
    assert missing_denials(load(OVERNIGHT), schema) == []


def test_the_project_settings_have_no_deny_rule_and_no_sandbox():
    settings = load(PROJECT)
    assert "deny" not in settings["permissions"]
    assert "sandbox" not in settings


FORBIDDEN = [
    "tools/rebuild-ghidra.sh",
    "tools/delink.sh",
    "tools/create-functions.sh",
    "gh pr merge 120 --merge",
    "uv run python -m bodecomp.sync apply",
    "uv run python -m bodecomp.sync --accept-ghidra-names apply",
    "uv run python -m bodecomp.names set 0x00011000 Foo src/game/a.cpp",
    "uv run python -m bodecomp.names --symbols config/symbols.txt set 0x1 A b",
    "uv run python -m bodecomp.libmatch",
    "uv run python -m bodecomp.libmatch --libs tools/xdk/xbox/lib",
    "git push --force origin match/night-2026-11-25",
    "git push -f origin match/night-2026-11-25",
    "git push origin match/night-2026-11-25 --force",
    "git push origin match/night-2026-11-25 -f",
    "git push --force-with-lease origin match/night-2026-11-25",
    "git push origin main",
    "git push -u origin main",
    "git push origin HEAD:main",
    "git push origin +main",
    "git push origin match/night-2026-11-25:refs/heads/main",
    "ln -sf /a /b",
    "ln -s -f /a /b",
    "ln -s --force /a /b",
]
WT = "../bustin-out-recomp-night-1"
ROUTINE = [
    "uv run python -m bodecomp.overnight status",
    "uv run python -m bodecomp.match --check",
    "uv run python -m bodecomp.match candidates 20 --min-size 17",
    "uv run python -m bodecomp.findings check",
    "uv run python -m bodecomp.ledger --check",
    "uv run python -m bodecomp.names check",
    "uv run python -m bodecomp.names stated",
    "uv run python -m bodecomp.sync check",
    "uv run python -m bodecomp.sync freshness",
    "uv run pytest -q",
    "uv run ruff check .",
    f"git worktree add {WT} -b night/1 match/night-2026-11-25",
    f"git worktree remove {WT}",
    f'ln -s "$PWD/build/target" "{WT}/build/target"',
    f'ln -s "$PWD/build/strings.tsv" "{WT}/build/strings.tsv"',
    f'ln -s "$PWD/orig" "{WT}/orig"',
    f'ln -s "$PWD/tools/wibo" "{WT}/tools/wibo"',
    f'ln -s "$PWD/tools/xdk" "{WT}/tools/xdk"',
]
# Commands that no allow rule names, so auto mode judges them, and that no deny
# rule may block.
NOT_DENIED = [
    "git push -u origin match/night-2026-11-25",
    "git push origin match/night-2026-11-25-2",
    "gh pr create --draft --title 'match: night run 2026-11-25'",
    "gh pr ready match/night-2026-11-25",
]


def rule_matches(rule: str, command: str) -> bool:
    """Match a command with a Bash(...) rule as Claude Code reads it.

    A rule that ends in " *" matches its prefix alone or followed by a space and
    any text. Any other * matches any text, also none.
    """
    body = rule.removeprefix("Bash(").removesuffix(")")
    tail = ""
    if body.endswith(" *"):
        body, tail = body[:-2], "( .*)?"
    pattern = ".*".join(re.escape(part) for part in body.split("*")) + tail
    return re.fullmatch(pattern, command, re.DOTALL) is not None


def bash_rules(kind: str) -> list[str]:
    rules = load(OVERNIGHT)["permissions"][kind]
    return [rule for rule in rules if rule.startswith("Bash(")]


def test_the_rule_matcher_reads_wildcards():
    assert rule_matches("Bash(ls *)", "ls")
    assert rule_matches("Bash(ls *)", "ls -la")
    assert not rule_matches("Bash(ls *)", "lsof")
    assert rule_matches("Bash(git push * main)", "git push origin main")
    assert not rule_matches("Bash(git push * main)", "git push origin main-2")
    assert rule_matches("Bash(a*b)", "ab")


@pytest.mark.parametrize("command", FORBIDDEN)
def test_a_deny_rule_matches_each_forbidden_command(command):
    assert any(rule_matches(rule, command) for rule in bash_rules("deny"))


@pytest.mark.parametrize("command", ROUTINE)
def test_routine_commands_are_allowed_and_not_denied(command):
    assert any(rule_matches(rule, command) for rule in bash_rules("allow"))
    denied = [rule for rule in bash_rules("deny") if rule_matches(rule, command)]
    assert denied == []


@pytest.mark.parametrize("command", NOT_DENIED)
def test_run_branch_pushes_and_the_draft_are_not_denied(command):
    denied = [rule for rule in bash_rules("deny") if rule_matches(rule, command)]
    assert denied == []
