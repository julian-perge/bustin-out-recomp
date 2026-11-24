struct S_001BFBD0
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfbd0(bool on);
};

// 0x001BFBD0
void S_001BFBD0::FUN_001bfbd0(bool on)
{
    flags &= ~0x400;
    if (on)
        flags |= 0x400;
}
