from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

API = os.environ.get("GHIDRA_MCP_URL", "http://127.0.0.1:8089")


class GhidraError(RuntimeError):
    pass


def get(path: str, **params) -> dict:
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=600) as response:
        result = json.load(response)
    if isinstance(result, dict) and "error" in result:
        raise GhidraError(f"{path}: {result['error']}")
    return result


def post(path: str, body: dict) -> dict:
    request = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.load(response)
    if isinstance(result, dict) and "error" in result:
        raise GhidraError(f"{path}: {result['error']}")
    return result


def _paged(path: str, key: str, **params) -> list:
    items, offset = [], 0
    while True:
        page = get(path, offset=offset, limit=1000, **params)
        items += page[key]
        offset += len(page[key])
        if not page[key] or offset >= page["total"]:
            return items


def list_functions() -> list[dict]:
    listed = [f for f in _paged("/find_functions", "functions") if not f["is_external"]]
    out = []
    for i in range(0, len(listed), 20):
        batch = listed[i : i + 20]
        refs = ",".join("0x" + f["address"] for f in batch)
        info = get("/get_functions", functions=refs, fields="body_start,body_end")
        for f in batch:
            detail = info["functions"]["0x" + f["address"]]
            out.append(
                {
                    "address": int(f["address"], 16),
                    "name": f["name"],
                    "size": detail["size"],
                    "is_thunk": f["is_thunk"],
                }
            )
    return out


def list_named_globals() -> list[tuple[int, str]]:
    from bodecomp.sync import parse_data_item, parse_global

    lines = _paged(
        "/list_globals", "globals", filter="defined", include_all_sections="true"
    )
    found = dict(g for g in (parse_global(line) for line in lines) if g is not None)
    # list_globals only covers the global namespace; data_items also holds the
    # labels the XBE loader put in library namespaces such as D3D and XAPILIB.
    items = get("/list_program_items", kind="data_items", limit=0)["items"]
    for item in items:
        parsed = parse_data_item(item)
        if parsed is not None:
            found.setdefault(*parsed)
    return sorted(found.items())


def rename(address: int, kind: str, name: str) -> None:
    if kind == "function":
        body = {"old_name": f"0x{address:08x}", "new_name": name, "strict_mode": "off"}
        try:
            post("/rename_function", body)
        except GhidraError as error:
            # Ghidra's own Function ID analysis leaves secondary labels at a
            # function's address, and a rename onto one of those names fails.
            # Removing that label lets the function take the name.
            if "already exists at this address" not in str(error):
                raise
            post("/delete_label", {"address": f"0x{address:08x}", "name": name})
            post("/rename_function", body)
    else:
        post(
            "/rename_symbol",
            {"target": f"0x{address:08x}", "new_name": name, "strict_mode": "off"},
        )


def define_data(address: int) -> None:
    post(
        "/apply_data_type",
        {
            "address": f"0x{address:08x}",
            "type_name": "undefined1",
            "clear_existing": False,
            "strict_mode": "off",
        },
    )


def save() -> None:
    get("/save_program")
