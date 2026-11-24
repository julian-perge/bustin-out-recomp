struct S_001BFB00
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfb00(bool on);
};

// 0x001BFB00
void S_001BFB00::FUN_001bfb00(bool on)
{
    flags &= ~2u;
    if (on)
        flags |= 2;
}
