import struct

SECTOR = 2048
MAGIC = b"MICROSOFT*XBOX*MEDIA"
ROOT_SECTOR = 33


def _entry_size(name: str) -> int:
    return (14 + len(name) + 3) // 4 * 4


def build_image(files: list[tuple[str, bytes]]) -> bytes:
    offsets = []
    cursor = 0
    for name, _ in files:
        offsets.append(cursor)
        cursor += _entry_size(name)
    table = bytearray(cursor)

    data_sector = ROOT_SECTOR + 1
    payload = bytearray()
    for i, (name, data) in enumerate(files):
        left = 2 * i + 1
        right = 2 * i + 2
        left_off = offsets[left] // 4 if left < len(files) else 0
        right_off = offsets[right] // 4 if right < len(files) else 0
        sector = data_sector + len(payload) // SECTOR
        struct.pack_into(
            "<HHIIBB",
            table,
            offsets[i],
            left_off,
            right_off,
            sector,
            len(data),
            0x20,
            len(name),
        )
        table[offsets[i] + 14 : offsets[i] + 14 + len(name)] = name.encode("ascii")
        payload += data
        payload += bytes(-len(payload) % SECTOR)

    image = bytearray(data_sector * SECTOR)
    vd = 32 * SECTOR
    image[vd : vd + 20] = MAGIC
    struct.pack_into("<II", image, vd + 20, ROOT_SECTOR, len(table))
    image[ROOT_SECTOR * SECTOR : ROOT_SECTOR * SECTOR + len(table)] = table
    return bytes(image + payload)
