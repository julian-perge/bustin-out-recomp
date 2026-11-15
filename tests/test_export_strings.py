import os
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools/export-strings.sh"


def closed_url() -> str:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def fake_ghidra(tmp_path: Path, output: str) -> Path:
    home = tmp_path / "ghidra"
    support = home / "support"
    support.mkdir(parents=True)
    tool = support / "analyzeHeadless"
    tool.write_text(f"#!/bin/bash\ncat <<'EOF'\n{output}\nEOF\n")
    tool.chmod(0o755)
    return home


def run(tmp_path: Path, url: str, home: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "GHIDRA_MCP_URL": url, "GHIDRA_HOME": str(home)}
    return subprocess.run(
        [str(SCRIPT), str(tmp_path / "strings.tsv")],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_refuses_while_the_server_is_up(tmp_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        result = run(tmp_path, f"http://127.0.0.1:{server.server_port}", tmp_path)
    finally:
        server.shutdown()
    assert result.returncode == 1
    assert "Stop the ghidra-mcp server first" in result.stderr


def test_prints_the_count_line(tmp_path):
    home = fake_ghidra(
        tmp_path,
        "INFO  ExportStringRefs.java> string references 3 in 2 functions"
        " (GhidraScript)",
    )
    result = run(tmp_path, closed_url(), home)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "string references 3 in 2 functions"


def test_shows_the_script_error_when_the_count_is_missing(tmp_path):
    home = fake_ghidra(tmp_path, "ERROR SCRIPT ERROR boom")
    result = run(tmp_path, closed_url(), home)
    assert result.returncode == 1
    assert "boom" in result.stderr
