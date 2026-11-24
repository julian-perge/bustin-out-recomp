struct S_001BFBB0
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfbb0(bool on);
};

// 0x001BFBB0
void S_001BFBB0::FUN_001bfbb0(bool on)
{
    flags &= ~0x80u;
    if (on)
        flags |= 0x80;
}
