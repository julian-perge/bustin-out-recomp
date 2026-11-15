from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

PREFIX = "mcp__ghidra-mcp__"
# The bridge registers these tools itself, outside the server's schema, and they
# only report what exists. load_tool_group and connect_instance are left out
# because .mcp.json loads every group at connect (F-0023) and they change what the
# bridge serves to every session.
DISCOVERY = (
    "check_tools",
    "list_instances",
    "list_tool_groups",
    "search_tools",
)
START, END = "# ghidra-read:start", "# ghidra-read:end"
AGENTS = (Path(".claude/agents/matcher.md"), Path(".claude/agents/reviewer.md"))
SETTINGS = Path(".claude/settings.json")
SNAPSHOT = (
    Path.home()
    / "git/bethington/ghidra-mcp/tests/conformance/snapshots/mcp_schema.snap"
)
URL = os.environ.get("GHIDRA_MCP_URL", "http://127.0.0.1:8089")


def tool_name(path: str) -> str:
    # This mirrors sanitize_tool_name in ghidra-mcp's
    # python/bridge_mcp_ghidra/validation.py, so the names match what the bridge
    # registers.
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", path.lower())
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:64].rstrip("_")


def read_only_tools(schema: dict) -> list[str]:
    names = {
        PREFIX + tool_name(tool["path"])
        for tool in schema["tools"]
        if tool.get("read_only") is True
    }
    names |= {PREFIX + name for name in DISCOVERY}
    return sorted(names)


def replace_block(text: str, items: list[str]) -> str:
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.strip() == START]
    ends = [i for i, line in enumerate(lines) if line.strip() == END]
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise ValueError(f"expected one '{START}' line followed by one '{END}' line")
    marker = lines[starts[0]]
    indent = marker[: len(marker) - len(marker.lstrip())]
    body = [f"{indent}- {item}\n" for item in items]
    return "".join(lines[: starts[0] + 1] + body + lines[ends[0] :])


def update_settings(settings: dict, tools: list[str]) -> dict:
    out = json.loads(json.dumps(settings))
    allow = out.setdefault("permissions", {}).setdefault("allow", [])
    out["permissions"]["allow"] = [a for a in allow if not a.startswith(PREFIX)] + list(
        tools
    )
    return out


def fetch_schema(url: str, timeout: float = 5) -> dict:
    with urllib.request.urlopen(f"{url}/mcp/schema", timeout=timeout) as response:
        return json.load(response)


def load_schema(url: str, snapshot: Path) -> tuple[dict, str]:
    try:
        return fetch_schema(url), url
    except OSError:
        return json.loads(snapshot.read_text()), str(snapshot)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bodecomp.agent_tools")
    parser.add_argument("--url", default=URL)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args(argv)
    schema, source = load_schema(args.url, args.snapshot)
    tools = read_only_tools(schema)
    for agent in AGENTS:
        agent.write_text(replace_block(agent.read_text(), tools))
    settings = update_settings(json.loads(SETTINGS.read_text()), tools)
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"{len(tools)} read-only tools from {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
