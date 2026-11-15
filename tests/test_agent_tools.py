import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from bodecomp.agent_tools import (
    fetch_schema,
    load_schema,
    read_only_tools,
    replace_block,
    tool_name,
    update_settings,
)

SCHEMA = {
    "count": 5,
    "tools": [
        {"path": "/get_xrefs_to", "read_only": True, "destructive": False},
        {"path": "/rename_function", "read_only": False, "destructive": False},
        {"path": "/debugger/status", "read_only": True, "destructive": False},
        {"path": "/delete_function", "read_only": False, "destructive": True},
        {"path": "/unclassified_tool"},
    ],
}


def test_tool_name_follows_the_bridge_rule():
    assert tool_name("/debugger/status") == "debugger_status"
    assert tool_name("/Get_Xrefs_To") == "get_xrefs_to"
    assert tool_name("/mcp/health") == "mcp_health"


def test_only_read_only_tools_are_listed():
    tools = read_only_tools(SCHEMA)
    assert "mcp__ghidra-mcp__get_xrefs_to" in tools
    assert "mcp__ghidra-mcp__debugger_status" in tools
    assert not any(
        word in tool
        for tool in tools
        for word in ("rename_function", "delete_function", "unclassified")
    )
    assert "mcp__ghidra-mcp__search_tools" in tools
    assert "mcp__ghidra-mcp__load_tool_group" not in tools
    assert "mcp__ghidra-mcp__connect_instance" not in tools
    assert tools == sorted(set(tools))


AGENT = (
    "---\nname: matcher\ntools:\n  - Read\n  # ghidra-read:start\n"
    "  - old\n  # ghidra-read:end\n---\nBody\n"
)


def test_replace_block_rewrites_only_between_markers():
    out = replace_block(AGENT, ["a", "b"])
    assert out == (
        "---\nname: matcher\ntools:\n  - Read\n  # ghidra-read:start\n"
        "  - a\n  - b\n  # ghidra-read:end\n---\nBody\n"
    )
    assert replace_block(out, ["a", "b"]) == out


def test_missing_markers_are_an_error():
    with pytest.raises(ValueError, match="ghidra-read:start"):
        replace_block("tools:\n  - Read\n", ["a"])


def test_update_settings_keeps_other_entries():
    settings = {
        "hooks": {"SessionStart": []},
        "permissions": {
            "allow": ["Bash(tools/session-start.sh)", "mcp__ghidra-mcp__old"]
        },
    }
    out = update_settings(settings, ["mcp__ghidra-mcp__a"])
    assert out == {
        "hooks": {"SessionStart": []},
        "permissions": {
            "allow": ["Bash(tools/session-start.sh)", "mcp__ghidra-mcp__a"]
        },
    }
    assert settings["permissions"]["allow"][1] == "mcp__ghidra-mcp__old"
    assert update_settings(out, ["mcp__ghidra-mcp__a"]) == out


def test_fetch_schema_reads_the_live_server():
    body = json.dumps(SCHEMA).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == "/mcp/schema" else 404)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert fetch_schema(f"http://127.0.0.1:{server.server_port}") == SCHEMA
    finally:
        server.shutdown()


def test_load_schema_falls_back_to_the_snapshot(tmp_path):
    snapshot = tmp_path / "mcp_schema.snap"
    snapshot.write_text(json.dumps(SCHEMA))
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    schema, source = load_schema(f"http://127.0.0.1:{port}", snapshot)
    assert schema == SCHEMA
    assert source == str(snapshot)
