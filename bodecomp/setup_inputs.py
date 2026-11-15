from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from bodecomp.xbe import Xbe
from bodecomp.xdvdfs import XGD1_PARTITION, extract

EXPECTED_XBE_SHA256 = "c11eea3a1d5cbe932892bfb25e425d12cec229b9fc471563f1e368d607706725"


def install_xbe(
    iso: Path,
    dest: Path,
    expected: str = EXPECTED_XBE_SHA256,
    partition: int = XGD1_PARTITION,
) -> str:
    staging = dest.with_suffix(".tmp")
    extract(iso, "default.xbe", staging, partition)
    digest = hashlib.sha256(staging.read_bytes()).hexdigest()
    if digest != expected:
        staging.unlink()
        raise ValueError(
            f"default.xbe SHA-256 is {digest}, expected {expected}. "
            "This is not the supported retail disc."
        )
    staging.replace(dest)
    return digest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iso", type=Path, required=True)
    parser.add_argument("--dest", type=Path, default=Path("orig/default.xbe"))
    args = parser.parse_args(argv)

    digest = install_xbe(args.iso, args.dest)
    xbe = Xbe.parse(args.dest.read_bytes())
    print(f"installed {args.dest} sha256 {digest}")
    print(f"title id 0x{xbe.title_id:08X}, entry 0x{xbe.entry:08X}")
    for lib in xbe.libraries:
        print(f"  {lib.name:8s} {lib.major}.{lib.minor}.{lib.build}")


if __name__ == "__main__":
    main()
