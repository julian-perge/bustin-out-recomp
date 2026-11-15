from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

WIBO = Path("tools/wibo/wibo")
CL = Path("tools/xdk/xbox/bin/vc71/CL.Exe")
BASE_FLAGS = ("/nologo", "/c", "/TP")


class ToolchainMissing(RuntimeError):
    pass


@dataclass(frozen=True)
class CompileResult:
    ok: bool
    output: Path
    log: str


def check_toolchain(root: Path) -> None:
    for path in (WIBO, CL):
        if not (root / path).exists():
            raise ToolchainMissing(
                f"{path.as_posix()} is missing. "
                "Run: uv run python -m bodecomp.setup_xdk"
            )


def build_command(source: Path, output: Path, flags: Sequence[str]) -> list[str]:
    return [
        WIBO.as_posix(),
        CL.as_posix(),
        *BASE_FLAGS,
        *flags,
        f"/Fo{output.as_posix()}",
        source.as_posix(),
    ]


def compile_cpp(
    root: Path,
    source: Path,
    output: Path,
    flags: Sequence[str],
    timeout: float = 120,
) -> CompileResult:
    check_toolchain(root)
    (root / output).parent.mkdir(parents=True, exist_ok=True)
    (root / output).unlink(missing_ok=True)
    try:
        proc = subprocess.run(
            build_command(source, output, flags),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(False, output, f"compile timed out after {timeout} s")
    except OSError as error:
        return CompileResult(False, output, f"compiler could not start: {error}")
    log = proc.stdout + proc.stderr
    return CompileResult(proc.returncode == 0 and (root / output).exists(), output, log)


def compiler_version(root: Path) -> str:
    check_toolchain(root)
    proc = subprocess.run(
        [WIBO.as_posix(), CL.as_posix()], cwd=root, capture_output=True, text=True
    )
    match = re.search(r"Version (\d+\.\d+\.\d+)", proc.stdout + proc.stderr)
    if not match:
        raise RuntimeError(
            f"CL.Exe printed no version banner:\n{proc.stdout}{proc.stderr}"
        )
    return match.group(1)
