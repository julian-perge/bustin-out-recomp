import re
import subprocess
from pathlib import Path

from bodecomp import setup_xdk

ROOT = Path(__file__).resolve().parent.parent
USER_HOME = re.compile(rb"(/Users/|/home/)[A-Za-z0-9._-]+")


def test_tracked_files_name_no_user_home_directory():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    hits = []
    for name in tracked:
        path = ROOT / name
        if not path.is_file():
            continue
        match = USER_HOME.search(path.read_bytes())
        if match:
            hits.append(f"{name}: {match.group().decode()}")
    assert hits == []


def test_default_xdk_archive_is_relative_to_the_repo():
    assert not setup_xdk.DEFAULT_ARCHIVE.is_absolute()
