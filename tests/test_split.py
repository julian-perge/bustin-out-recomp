from bodecomp.split import Unit, partition, read_units, write_units


def test_partition_covers_every_byte_once():
    units = partition(0x11000, 0x11100, [0x11080, 0x11010, 0x11010, 0x20000])
    assert units == [
        Unit(0x11000, 0x11010),
        Unit(0x11010, 0x11080),
        Unit(0x11080, 0x11100),
    ]


def test_units_file_round_trip(tmp_path):
    path = tmp_path / "units.txt"
    units = [Unit(0x11000, 0x11010), Unit(0x11010, 0x11100)]
    write_units(path, units)
    assert path.read_text() == "00011000 00011010\n00011010 00011100\n"
    assert read_units(path) == units
