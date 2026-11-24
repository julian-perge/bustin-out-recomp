import json
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
