import os
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools/session-start.sh"
STATUS = (
    "# Status\n\nIntro.\n\n<!-- active:start -->\n"
    "- Next action: write the M2 plan.\n<!-- active:end -->\n"
)
FINDINGS = (
    "# Findings\n\n## F-0001 Done thing\n- Status: confirmed\n\n"
    "## F-0002 Open thing\n- Status: open\n"
)


def project(tmp_path: Path, status: str | None = STATUS) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    if status is not None:
        (docs / "STATUS.md").write_text(status)
    (docs / "FINDINGS.md").write_text(FINDINGS)

    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-C", str(tmp_path), *args], check=True, capture_output=True
        )

    git("init", "-q", "-b", "main")
    git("add", "docs")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "docs")
    return tmp_path


def closed_url() -> str:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def run(root: Path, url: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root), "GHIDRA_MCP_URL": url}
    return subprocess.run(
        [str(SCRIPT)], env=env, capture_output=True, text=True, timeout=120
    )


def test_prints_the_active_block_and_open_findings(tmp_path):
    result = run(project(tmp_path), closed_url())
    assert result.returncode == 0
    out = result.stdout
    assert "- Next action: write the M2 plan." in out
    assert "active:start" not in out and "Intro." not in out
    assert "F-0002 open: Open thing" in out
    assert "F-0001" not in out
    assert "ghidra-mcp: down" in out
    assert "branch: main, uncommitted: 0" in out
    assert len(out.splitlines()) <= 40


def test_reports_the_server_when_it_answers(tmp_path):
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
        url = f"http://127.0.0.1:{server.server_port}"
        assert f"ghidra-mcp: up at {url}" in run(project(tmp_path), url).stdout
    finally:
        server.shutdown()


def test_missing_status_file_still_exits_zero(tmp_path):
    result = run(project(tmp_path, status=None), closed_url())
    assert result.returncode == 0
    assert "(docs/STATUS.md is missing)" in result.stdout


def test_many_open_findings_stay_within_forty_lines(tmp_path):
    root = project(tmp_path)
    many = "".join(f"## F-{i:04d} T{i}\n- Status: open\n\n" for i in range(1, 60))
    (root / "docs/FINDINGS.md").write_text(many)
    out = run(root, closed_url()).stdout
    assert "... and 47 more" in out
    assert len(out.splitlines()) <= 40
