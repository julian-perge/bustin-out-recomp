import os
import shutil
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools/session-start.sh"
FINDINGS = (
    "# Findings\n\n## F-0001 Done thing\n- Status: confirmed\n\n"
    "## F-0002 Open thing\n- Status: open\n"
)

# The hook may use only these tools. A test that needs one missing leaves it out.
HOOK_TOOLS = [
    "bash", "cat", "curl", "cut", "dirname", "find", "git", "grep", "head", "mkdir",
    "pgrep", "sed", "sort", "timeout", "tr", "uv", "wc",
]  # fmt: skip

FAKE_GH = """#!/bin/bash
# Prints the file that the test put in $FAKE_DIR for the query that the hook asks.
args="$*"
echo "$args" >>"$FAKE_DIR/gh-calls"
if [ -e "$FAKE_DIR/gh-fails" ]; then echo "gh: not signed in" >&2; exit 1; fi
case "$args" in
  *"--label ghidra-writer"*) name=writers ;;
  *"--state merged"*) name=merged ;;
  "pr list"*) name=prs ;;
  "issue list"*) name=issues ;;
  *) exit 2 ;;
esac
cat "$FAKE_DIR/$name" 2>/dev/null
exit 0
"""

FAKE_AGENT_SKILLS = """#!/bin/bash
cat "$FAKE_DIR/next" 2>/dev/null
exit 0
"""

FAKE_PGREP = """#!/bin/bash
# Reports a process only for the pattern in $FAKE_RUNNING.
for last; do :; done
if [ "$last" = "${FAKE_RUNNING:-}" ]; then echo 4242; exit 0; fi
exit 1
"""


def project(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
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


class Sources:
    """A PATH that holds the real hook tools and fakes of gh, agent-skills and pgrep."""

    def __init__(self, tmp_path: Path):
        self.fake_dir = tmp_path / "fake"
        self.fake_dir.mkdir()
        self.bin = tmp_path / "bin"
        self.bin.mkdir()
        for tool in HOOK_TOOLS:
            real = shutil.which(tool)
            assert real, f"{tool} is not installed"
            (self.bin / tool).symlink_to(real)
        (self.bin / "pgrep").unlink()
        self.install("pgrep", FAKE_PGREP)
        self.install("gh", FAKE_GH)
        self.install("agent-skills", FAKE_AGENT_SKILLS)

    def install(self, name: str, text: str) -> None:
        path = self.bin / name
        path.write_text(text)
        path.chmod(0o755)

    def remove(self, name: str) -> None:
        (self.bin / name).unlink()

    def put(self, name: str, text: str) -> None:
        (self.fake_dir / name).write_text(text)

    def env(self, root: Path, url: str, **extra: str) -> dict[str, str]:
        return {
            "PATH": str(self.bin),
            "HOME": os.environ["HOME"],
            "FAKE_DIR": str(self.fake_dir),
            "CLAUDE_PROJECT_DIR": str(root),
            "GHIDRA_MCP_URL": url,
            "BODECOMP_HOOK_CACHE": str(self.fake_dir.parent / "cache"),
            **extra,
        }


def run(root: Path, url: str, sources: Sources, **extra: str):
    return subprocess.run(
        [str(SCRIPT)],
        env=sources.env(root, url, **extra),
        capture_output=True,
        text=True,
        timeout=120,
    )


def full_sources(tmp_path: Path) -> Sources:
    sources = Sources(tmp_path)
    sources.put("writers", "#61 T4: point the agents (julian-perge)\n")
    sources.put("prs", "#70 feat: the hook (feat/60-x)\n#71 docs: a note (docs/y)\n")
    sources.put("issues", "#60 T3: generate the block\n")
    sources.put("merged", "#69 Merge pull request #69 from x\n")
    sources.put(
        "next",
        "# What to do next\n\n| # | Title | Command |\n| --- | --- | --- |\n"
        "| #30 (frontier) | one | `/agent-skills:build #30` |\n"
        "| #31 (frontier) | two | `/agent-skills:build #31` |\n",
    )
    return sources


def test_prints_every_source(tmp_path):
    sources = full_sources(tmp_path)
    result = run(
        project(_repo(tmp_path)),
        closed_url(),
        sources,
        FAKE_RUNNING="GhidraMCPHeadlessServer",
    )
    assert result.returncode == 0
    out = result.stdout
    assert "branch: main, uncommitted: 0" in out
    assert "ghidra-mcp: down" in out
    assert "running: ghidra-mcp server (pid 4242)" in out
    assert "ghidra writer: #61 T4: point the agents (julian-perge)" in out
    assert "warning" not in out.lower()
    assert "open pull requests:" in out
    assert "  #70 feat: the hook (feat/60-x)" in out
    assert "assigned issues:" in out
    assert "  #60 T3: generate the block" in out
    assert "next:" in out
    assert "  /agent-skills:build #30 (frontier)" in out
    assert "last merged pull request: #69 Merge pull request #69 from x" in out
    assert "F-0002 open: Open thing" in out
    assert "F-0001" not in out
    assert len(out.splitlines()) <= 40


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


def test_no_process_and_no_writer_say_none(tmp_path):
    sources = Sources(tmp_path)
    result = run(project(_repo(tmp_path)), closed_url(), sources)
    assert result.returncode == 0
    assert "running: none" in result.stdout
    assert "ghidra writer: none" in result.stdout
    assert "open pull requests: none" in result.stdout
    assert "assigned issues: none" in result.stdout


def test_gh_missing_prints_one_line_per_source_and_goes_on(tmp_path):
    sources = full_sources(tmp_path)
    sources.remove("gh")
    result = run(project(_repo(tmp_path)), closed_url(), sources)
    assert result.returncode == 0
    out = result.stdout
    for source in (
        "ghidra writer",
        "open pull requests",
        "assigned issues",
        "last merged pull request",
    ):
        assert f"{source}: unavailable (gh is not installed)" in out
    assert "next:" in out
    assert "F-0002 open: Open thing" in out
    assert "branch: main, uncommitted: 0" in out
    assert len(out.splitlines()) <= 40


def test_gh_failing_prints_one_line_per_source(tmp_path):
    sources = full_sources(tmp_path)
    sources.put("gh-fails", "")
    result = run(project(_repo(tmp_path)), closed_url(), sources)
    assert result.returncode == 0
    assert "ghidra writer: unavailable (gh failed)" in result.stdout
    assert "last merged pull request: unavailable (gh failed)" in result.stdout
    assert len(result.stdout.splitlines()) <= 40


def test_agent_skills_missing_prints_one_line_and_goes_on(tmp_path):
    sources = full_sources(tmp_path)
    sources.remove("agent-skills")
    result = run(project(_repo(tmp_path)), closed_url(), sources)
    assert result.returncode == 0
    out = result.stdout
    assert "next: unavailable (agent-skills is not installed)" in out
    assert "ghidra writer: #61" in out
    assert len(out.splitlines()) <= 40


def test_two_assigned_ghidra_writer_tasks_print_a_warning(tmp_path):
    sources = full_sources(tmp_path)
    sources.put(
        "writers",
        "#61 T4: point the agents (julian-perge)\n#62 T5: find Ghidra (someone)\n",
    )
    result = run(project(_repo(tmp_path)), closed_url(), sources)
    assert result.returncode == 0
    out = result.stdout
    assert "WARNING: 2 open ghidra-writer tasks are assigned" in out
    assert "#61 T4: point the agents (julian-perge)" in out
    assert "#62 T5: find Ghidra (someone)" in out
    assert len(out.splitlines()) <= 40


def test_long_lists_are_capped_to_forty_lines(tmp_path):
    sources = full_sources(tmp_path)
    many = "".join(f"#{i} title {i}\n" for i in range(100, 160))
    sources.put("prs", many)
    sources.put("issues", many)
    sources.put("writers", many)
    sources.put("next", "".join(f"| #{i} (frontier) | t | `c` |\n" for i in range(60)))
    root = project(_repo(tmp_path))
    (root / "docs/FINDINGS.md").write_text(
        "".join(f"## F-{i:04d} T{i}\n- Status: open\n\n" for i in range(1, 60))
    )
    result = run(root, closed_url(), sources)
    assert result.returncode == 0
    assert "... and 47 more" in result.stdout
    assert len(result.stdout.splitlines()) <= 40


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
        sources = Sources(tmp_path)
        out = run(project(_repo(tmp_path)), url, sources).stdout
        assert f"ghidra-mcp: up at {url}" in out
    finally:
        server.shutdown()


def test_a_second_run_within_a_minute_does_not_call_gh_again(tmp_path):
    sources = full_sources(tmp_path)
    root = project(_repo(tmp_path))
    first = run(root, closed_url(), sources)
    calls = (sources.fake_dir / "gh-calls").read_text().splitlines()
    assert len(calls) == 4
    sources.put("merged", "#99 something newer\n")
    second = run(root, closed_url(), sources)
    assert (sources.fake_dir / "gh-calls").read_text().splitlines() == calls
    assert second.stdout == first.stdout
