import os
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools/create-functions.sh"


def closed_url() -> str:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def run(address_list: Path, url: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "GHIDRA_MCP_URL": url}
    return subprocess.run(
        [str(SCRIPT), str(address_list)],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_refuses_without_an_address_list(tmp_path):
    result = run(tmp_path / "missing.txt", closed_url())
    assert result.returncode == 1
    assert "Write the address list first" in result.stderr


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
    address_list = tmp_path / "list.txt"
    address_list.write_text("00011030\n")
    try:
        result = run(address_list, f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 1
    assert "Stop the ghidra-mcp server first" in result.stderr
