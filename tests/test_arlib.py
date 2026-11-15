from bodecomp.arlib import members


def header(name: str, size: int) -> bytes:
    return (
        name.ljust(16).encode()
        + b"0".ljust(12)
        + b"".ljust(6)
        + b"".ljust(6)
        + b"0".ljust(8)
        + str(size).ljust(10).encode()
        + b"`\n"
    )


def archive(items: list[tuple[str, bytes]]) -> bytes:
    out = b"!<arch>\n"
    for name, body in items:
        out += header(name, len(body)) + body + (b"\n" if len(body) % 2 else b"")
    return out


def test_skips_linker_members_and_resolves_long_names():
    longnames = b"averyveryverylongname.obj\0"
    data = archive(
        [
            ("/", b"\0\0\0\0"),
            ("/", b"\0\0\0\0"),
            ("//", longnames),
            ("/0", b"ABC"),
            ("short.obj/", b"DE"),
        ]
    )
    assert members(data) == [
        ("averyveryverylongname.obj", b"ABC"),
        ("short.obj", b"DE"),
    ]
