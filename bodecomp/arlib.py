from __future__ import annotations

MAGIC = b"!<arch>\n"


def _long_name(longnames: bytes, offset: int) -> str:
    end = len(longnames)
    for terminator in (b"\0", b"/\n"):
        found = longnames.find(terminator, offset)
        if found != -1:
            end = min(end, found)
    return longnames[offset:end].decode("latin-1")


def members(data: bytes) -> list[tuple[str, bytes]]:
    if not data.startswith(MAGIC):
        raise ValueError("not an ar archive: the !<arch> magic is missing")
    out = []
    longnames = b""
    pos = len(MAGIC)
    while pos + 60 <= len(data):
        header = data[pos : pos + 60]
        raw_name = header[:16].decode("latin-1").rstrip()
        size = int(header[48:58].decode("ascii").strip())
        body = data[pos + 60 : pos + 60 + size]
        pos += 60 + size + (size & 1)
        if raw_name == "/":
            continue
        if raw_name == "//":
            longnames = body
            continue
        if raw_name.startswith("/") and raw_name[1:].isdigit():
            name = _long_name(longnames, int(raw_name[1:]))
        else:
            name = raw_name.rstrip("/")
        out.append((name, body))
    return out
