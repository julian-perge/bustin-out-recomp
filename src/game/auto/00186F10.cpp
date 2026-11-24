struct S_00186F10
{
    int pad;
    int p;
    unsigned n;
    unsigned FUN_00186f10();
};

// 0x00186F10
unsigned S_00186F10::FUN_00186f10()
{
    if (p)
        return ((n + 31) >> 3) & 0x1ffffffc;
    return 0;
}
