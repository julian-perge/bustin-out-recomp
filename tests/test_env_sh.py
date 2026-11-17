import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ENV_SH = ROOT / "tools" / "env.sh"
HOMEBREW_PATH = "/opt/homebrew"


def make_ghidra(prefix: Path, version: str) -> Path:
    home = prefix / "Cellar" / "ghidra" / version / "libexec"
    headless = home / "support" / "analyzeHeadless"
    headless.parent.mkdir(parents=True)
    headless.write_text("#!/bin/sh\n")
    headless.chmod(0o755)
    return home


def make_brew(bin_dir: Path, prefix: Path) -> None:
    bin_dir.mkdir(exist_ok=True)
    brew = bin_dir / "brew"
    brew.write_text(f'#!/bin/sh\necho "{prefix}"\n')
    brew.chmod(0o755)


def source_env(tmp_path: Path, **env) -> subprocess.CompletedProcess:
    base = {"PATH": f"{tmp_path / 'bin'}:/usr/bin:/bin", "HOME": str(tmp_path)}
    base.update(env)
    return subprocess.run(
        ["bash", "-c", f'set -euo pipefail; source "{ENV_SH}"; echo "$GHIDRA_HOME"'],
        capture_output=True,
        text=True,
        env=base,
    )


def test_existing_ghidra_home_wins(tmp_path):
    prefix = tmp_path / "brew"
    make_ghidra(prefix, "12.2")
    make_brew(tmp_path / "bin", prefix)
    result = source_env(tmp_path, GHIDRA_HOME="/somewhere/else")
    assert result.returncode == 0
    assert result.stdout.strip() == "/somewhere/else"


def test_brew_prefix_is_used_and_the_highest_version_wins(tmp_path):
    prefix = tmp_path / "brew"
    make_ghidra(prefix, "9.9")
    newest = make_ghidra(prefix, "12.10")
    make_ghidra(prefix, "12.2")
    make_brew(tmp_path / "bin", prefix)
    result = source_env(tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == str(newest)


def test_homebrew_prefix_is_used_when_brew_is_missing(tmp_path):
    prefix = tmp_path / "brew"
    home = make_ghidra(prefix, "12.2")
    (tmp_path / "bin").mkdir()
    result = source_env(tmp_path, HOMEBREW_PREFIX=str(prefix))
    assert result.returncode == 0
    assert result.stdout.strip() == str(home)


def test_missing_ghidra_exits_1_and_names_the_tried_paths(tmp_path):
    prefix = tmp_path / "brew"
    prefix.mkdir()
    make_brew(tmp_path / "bin", prefix)
    result = source_env(tmp_path)
    assert result.returncode == 1
    assert str(prefix) in result.stderr
    assert "support/analyzeHeadless" in result.stderr
    assert result.stdout == ""


def source_env_heap(tmp_path: Path, **env) -> subprocess.CompletedProcess:
    base = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "GHIDRA_HOME": "/g"}
    base.update(env)
    return subprocess.run(
        [
            "bash",
            "-c",
            f'set -euo pipefail; source "{ENV_SH}"; '
            'bash -c \'echo "$GHIDRA_HEADLESS_MAXMEM"\'',
        ],
        capture_output=True,
        text=True,
        env=base,
    )


def test_env_sh_exports_a_16g_headless_heap(tmp_path):
    result = source_env_heap(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "16G"


def test_an_existing_headless_heap_wins(tmp_path):
    result = source_env_heap(tmp_path, GHIDRA_HEADLESS_MAXMEM="6G")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "6G"


def test_the_server_script_takes_its_heap_from_env_sh():
    script = (ROOT / "tools" / "ghidra-mcp-headless.sh").read_text()
    assert "-Xmx$GHIDRA_HEADLESS_MAXMEM" in script
    assert "-Xmx4g" not in script


def test_no_tool_script_names_the_homebrew_path_except_env_sh():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "tools"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    hits = []
    for name in tracked:
        path = ROOT / name
        if name == "tools/env.sh" or not path.is_file():
            continue
        if HOMEBREW_PATH.encode() in path.read_bytes():
            hits.append(name)
    assert hits == []


def test_env_sh_finds_ghidra_on_this_machine():
    if shutil.which("brew") is None and not Path(HOMEBREW_PATH).is_dir():
        pytest.skip("no Homebrew on this machine")
    env = {k: v for k, v in os.environ.items() if k != "GHIDRA_HOME"}
    result = subprocess.run(
        [
            "bash",
            "-c",
            f'set -euo pipefail; source "{ENV_SH}"; '
            'test -x "$GHIDRA_HOME/support/analyzeHeadless"',
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
