from bodecomp.libmatch import LibFunction, classify, lib_functions
from bodecomp.symbols import Entry
from tests.coffbuild import build_coff
from tests.test_arlib import archive

FUNC = 0x20
EXTERNAL = 2

# mov eax, [g_value]; ret -- bytes 1..4 are an address the linker fills in.
LOAD_GLOBAL = b"\xa1\x00\x00\x00\x00\xc3"
LONG_BODY = bytes(range(0x10, 0x10 + 20)) + b"\xc3"
ALL = (True,) * len(LONG_BODY)


def entry(address, size, name=None):
    return Entry(address, "function", size, name or f"FUN_{address:08x}", "auto", "")


def reader(memory: dict[int, bytes]):
    def read(address, size):
        return memory[address][:size]

    return read


def test_lib_functions_mask_relocated_bytes():
    obj = build_coff(
        sections=[(".text", LOAD_GLOBAL, [(1, 1, 6)])],
        symbols=[("_get", 0, 1, FUNC, EXTERNAL), ("_g_value", 0, 0, 0, EXTERNAL)],
    )
    (f,) = lib_functions("libx.lib", archive([("get.obj/", obj)]))
    assert f.name == "_get"
    assert f.mask == (True, False, False, False, False, True)


def test_masked_match_names_the_function():
    mask = (True, False, False, False, False, True)
    lib = [LibFunction("_get", "libx.lib", "get.obj", LOAD_GLOBAL, mask)]
    target = b"\xa1\x10\x20\x30\x00\xc3"
    out = classify(
        [entry(0x21E000, 6)], reader({0x21E000: target}), lib, lambda a: True
    )
    assert out[0].name == "_get"
    assert out[0].tier == "sdk"
    assert out[0].evidence == "lib:libx.lib:get.obj"


def test_short_common_code_outside_sdk_is_not_claimed():
    lib = [LibFunction("_zero", "libx.lib", "z.obj", b"\x33\xc0\xc3", (True,) * 3)]
    out = classify(
        [entry(0x50000, 3)], reader({0x50000: b"\x33\xc0\xc3"}), lib, lambda a: False
    )
    assert out[0].tier == "auto"


def test_long_match_outside_sdk_is_claimed():
    lib = [LibFunction("_long", "libx.lib", "l.obj", LONG_BODY, ALL)]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: False,
    )
    assert out[0].name == "_long"


def test_same_bytes_under_several_names_is_ambiguous():
    lib = [LibFunction(n, "libx.lib", f"{n}.obj", LONG_BODY, ALL) for n in ("_b", "_a")]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: True,
    )
    assert out[0].name == "FUN_00050000"
    assert out[0].tier == "sdk"
    assert out[0].evidence == "lib-ambiguous(2):_a,_b"


def test_prefix_of_a_longer_function_is_not_a_match():
    lib = [LibFunction("_short", "libx.lib", "s.obj", LONG_BODY[:16], (True,) * 16)]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: True,
    )
    assert out[0].tier == "auto"


def test_trailing_padding_in_library_code_is_ignored():
    padded = LONG_BODY + b"\xcc\xcc"
    lib = [LibFunction("_long", "libx.lib", "l.obj", padded, (True,) * len(padded))]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: True,
    )
    assert out[0].name == "_long"


def test_replacing_a_loader_name_keeps_it_in_the_evidence():
    lib = [LibFunction("_CreateThread@24", "xapilib.lib", "thread.obj", LONG_BODY, ALL)]
    start = Entry(
        0x101000, "function", len(LONG_BODY), "CreateThread", "sdk", "xbe-loader"
    )
    out = classify([start], reader({0x101000: LONG_BODY}), lib, lambda a: True)
    assert out[0].name == "_CreateThread@24"
    assert out[0].evidence == "lib:xapilib.lib:thread.obj; was:CreateThread"


def test_only_the_libraries_the_xbe_links_are_used():
    from bodecomp.libmatch import libs_for_stamps

    assert libs_for_stamps(["XAPILIB", "D3D8", "XGRAPHC", "LIBCPMT"]) == [
        "xapilib.lib",
        "d3d8.lib",
        "xgraphics.lib",
        "libcpmt.lib",
    ]


def test_unknown_library_stamp_is_an_error():
    import pytest

    from bodecomp.libmatch import libs_for_stamps

    with pytest.raises(KeyError, match="XONLINE"):
        libs_for_stamps(["XAPILIB", "XONLINE"])


def test_ambiguous_match_outside_sdk_is_not_claimed():
    lib = [LibFunction(n, "libx.lib", f"{n}.obj", LONG_BODY, ALL) for n in ("_b", "_a")]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: False,
    )
    assert out[0].tier == "auto"
    assert out[0].evidence == ""


def test_ambiguous_evidence_counts_every_candidate():
    names = [f"_f{i}" for i in range(7)]
    lib = [LibFunction(n, "libx.lib", f"{n}.obj", LONG_BODY, ALL) for n in names]
    out = classify(
        [entry(0x50000, len(LONG_BODY))],
        reader({0x50000: LONG_BODY}),
        lib,
        lambda a: True,
    )
    assert out[0].evidence == "lib-ambiguous(7):_f0,_f1,_f2,_f3,_f4"


def test_running_again_keeps_the_earlier_evidence():
    lib = [LibFunction("_CreateThread@24", "xapilib.lib", "thread.obj", LONG_BODY, ALL)]
    named = Entry(
        0x101000,
        "function",
        len(LONG_BODY),
        "_CreateThread@24",
        "sdk",
        "lib:xapilib.lib:thread.obj; was:CreateThread",
    )
    out = classify([named], reader({0x101000: LONG_BODY}), lib, lambda a: True)
    assert out[0] == named


def test_running_again_keeps_a_name_made_unique_by_its_address():
    lib = [LibFunction("__flushall", "libcmt.lib", "fflush.obj", LONG_BODY, ALL)]
    named = Entry(
        0x224666,
        "function",
        len(LONG_BODY),
        "__flushall_00224666",
        "sdk",
        "lib:libcmt.lib:fflush.obj",
    )
    out = classify([named], reader({0x224666: LONG_BODY}), lib, lambda a: True)
    assert out[0] == named
