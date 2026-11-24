struct S_001BFAE0
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfae0(bool on);
};

// 0x001BFAE0
void S_001BFAE0::FUN_001bfae0(bool on)
{
    flags &= ~1u;
    if (on)
        flags |= 1;
}
