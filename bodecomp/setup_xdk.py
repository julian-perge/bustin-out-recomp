from __future__ import annotations

import argparse
import shutil
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

from bodecomp.cl import WIBO, compiler_version

DEFAULT_ARCHIVE = Path("xbox-sdks/2003-06 - 5558.2 - SDK.7z")
INSTALLER = "XDKSetup5558.2.exe"
WANTED = ("XDK/xbox/bin/vc71/*", "XDK/xbox/lib/*", "XDK/xbox/include/*")
WIBO_URL = "https://github.com/decompals/wibo/releases/download/1.2.0/wibo-macos"


def unpack_xdk(archive: Path, root: Path, work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run(["7zz", "x", "-y", f"-o{work}", str(archive), INSTALLER], check=True)
    subprocess.run(
        ["7zz", "x", "-y", f"-o{work}", str(work / INSTALLER), *WANTED], check=True
    )
    shutil.copytree(work / "XDK/xbox", root / "tools/xdk/xbox", dirs_exist_ok=True)


def install_wibo(root: Path) -> None:
    target = root / WIBO
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(WIBO_URL) as response:
        target.write_bytes(response.read())
    target.chmod(0o755)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path.home() / f"tmp/{date.today().isoformat()}-xdk-unpack",
    )
    args = parser.parse_args(argv)

    root = Path.cwd()
    unpack_xdk(args.archive, root, args.work_dir)
    install_wibo(root)
    print(f"CL.Exe version {compiler_version(root)}")


if __name__ == "__main__":
    main()
