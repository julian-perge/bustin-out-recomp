from pathlib import Path

import pytest

from bodecomp.cl import ToolchainMissing, build_command, check_toolchain, compile_cpp


def test_build_command_orders_wrapper_compiler_flags_output_source():
    cmd = build_command(Path("src/m0/a.cpp"), Path("build/m0/O2/a.obj"), ["/O2", "/G6"])
    assert cmd == [
        "tools/wibo/wibo",
        "tools/xdk/xbox/bin/vc71/CL.Exe",
        "/nologo",
        "/c",
        "/TP",
        "/O2",
        "/G6",
        "/Fobuild/m0/O2/a.obj",
        "src/m0/a.cpp",
    ]


def test_missing_toolchain_names_path_and_setup_command(tmp_path):
    with pytest.raises(ToolchainMissing) as info:
        check_toolchain(tmp_path)
    message = str(info.value)
    assert "tools/wibo/wibo" in message
    assert "bodecomp.setup_xdk" in message


def fake_toolchain(root: Path, wibo_script: str, executable: bool = True) -> None:
    wibo = root / "tools/wibo/wibo"
    wibo.parent.mkdir(parents=True)
    wibo.write_text(wibo_script)
    wibo.chmod(0o755 if executable else 0o644)
    cl = root / "tools/xdk/xbox/bin/vc71/CL.Exe"
    cl.parent.mkdir(parents=True)
    cl.write_bytes(b"")


def test_hung_compiler_becomes_a_failed_result(tmp_path):
    fake_toolchain(tmp_path, "#!/bin/sh\nsleep 5\n")
    result = compile_cpp(
        tmp_path, Path("a.cpp"), Path("build/a.obj"), ["/O2"], timeout=0.5
    )
    assert not result.ok
    assert "timed out" in result.log


def test_unlaunchable_wrapper_becomes_a_failed_result(tmp_path):
    fake_toolchain(tmp_path, "#!/bin/sh\nexit 0\n", executable=False)
    result = compile_cpp(tmp_path, Path("a.cpp"), Path("build/a.obj"), ["/O2"])
    assert not result.ok
    assert "could not start" in result.log
