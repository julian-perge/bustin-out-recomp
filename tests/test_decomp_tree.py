import json
import os
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools/decomp-tree.sh"


def closed_url() -> str:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def run(url: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "GHIDRA_MCP_URL": url, "DECOMP_TREE_POLL_SECONDS": "0"}
    return subprocess.run(
        [str(SCRIPT)], env=env, capture_output=True, text=True, timeout=60
    )


def fake_server(
    create: dict, run_reply: dict, phases: list[str], in_sync: list[bool] | None = None
):
    """Serve the three tree endpoints and record each request as (path, body)."""
    in_sync = in_sync or [True]
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def reply(self, body):
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            requests.append((self.path, None))
            if self.path.startswith("/check_connection"):
                self.reply({"status": "ok"})
            elif self.path.startswith("/decompile_tree_status"):
                phase = phases.pop(0) if len(phases) > 1 else phases[0]
                synced = in_sync.pop(0) if len(in_sync) > 1 else in_sync[0]
                self.reply(
                    {
                        "phase": phase,
                        "in_sync": synced,
                        "functions_total": 10,
                        "functions_done": 10 if phase == "complete" else 4,
                        "functions_failed": 0,
                    }
                )
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            requests.append((self.path, body))
            if self.path.startswith("/decompile_tree_create"):
                self.reply(create)
            elif self.path.startswith("/decompile_tree_run"):
                self.reply(run_reply)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, requests


def test_refuses_while_the_server_is_down():
    result = run(closed_url())
    assert result.returncode == 1
    assert "Start the ghidra-mcp server first" in result.stderr


def test_creates_the_tree_starts_the_sweep_and_waits_for_the_end():
    server, requests = fake_server(
        {"tree_id": "tree_1", "phase": "idle"},
        {"tree_id": "tree_1", "phase": "queued"},
        ["queued", "decompiling", "complete"],
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 0, result.stderr
    create = [r for r in requests if r[0].startswith("/decompile_tree_create")]
    assert create == [
        (
            "/decompile_tree_create?program=default.xbe",
            {"root": str(ROOT / "build/decomp-tree")},
        )
    ]
    assert ("/decompile_tree_run", {"tree": "tree_1", "action": "start"}) in requests
    statuses = [r for r in requests if r[0].startswith("/decompile_tree_status")]
    assert statuses[-1][0] == "/decompile_tree_status?tree=tree_1"
    assert len(statuses) == 3
    assert "10 of 10 functions" in result.stdout


def test_a_failed_sweep_exits_1():
    server, _ = fake_server(
        {"tree_id": "tree_1"}, {"phase": "queued"}, ["decompiling", "failed"]
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 1
    assert "failed" in result.stderr


def test_a_create_error_exits_1_with_the_message():
    server, requests = fake_server(
        {"error": "the root is not empty"}, {"phase": "queued"}, ["complete"]
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 1
    assert "the root is not empty" in result.stderr
    assert not [r for r in requests if r[0].startswith("/decompile_tree_run")]


def test_a_tree_that_is_already_in_sync_is_not_swept_again():
    server, requests = fake_server(
        {"tree_id": "tree_1", "phase": "complete", "in_sync": True},
        {"phase": "queued"},
        ["complete"],
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 0, result.stderr
    assert not [r for r in requests if r[0].startswith("/decompile_tree_run")]
    assert "already up to date" in result.stdout


def test_a_swept_tree_waits_for_the_reconcile_and_is_not_swept_again():
    # The real server queues a reconcile while it adopts a tree, so the create reply
    # says in_sync false even for a tree that matches the program.
    server, requests = fake_server(
        {"tree_id": "tree_1", "phase": "complete", "in_sync": False, "adopted": True},
        {"phase": "queued"},
        ["complete"],
        [False, False, True],
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 0, result.stderr
    assert not [r for r in requests if r[0].startswith("/decompile_tree_run")]
    statuses = [r for r in requests if r[0].startswith("/decompile_tree_status")]
    assert len(statuses) == 3
    assert "already up to date" in result.stdout


def test_a_tree_that_turns_stale_while_the_script_waits_exits_1():
    server, requests = fake_server(
        {"tree_id": "tree_1", "phase": "complete", "in_sync": False},
        {"phase": "queued"},
        ["complete", "stale"],
        [False],
    )
    try:
        result = run(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
    assert result.returncode == 1
    assert "became stale" in result.stderr
    assert not [r for r in requests if r[0].startswith("/decompile_tree_run")]
