// 0x001C0E90
short fn_001C0E90(short id)
{
    if (id >= 0 && id <= 0xff)
        return 0;
    if (id >= 0x100 && id <= 0xfff)
        return 1;
    if (id >= 0x2000 && id <= 0x2328)
        return 3;
    if (id >= 0x1000 && id <= 0x1fff)
        return 2;
    return 0;
}
