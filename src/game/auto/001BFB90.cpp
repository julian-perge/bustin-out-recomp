struct S_001BFB90
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfb90(bool on);
};

// 0x001BFB90
void S_001BFB90::FUN_001bfb90(bool on)
{
    flags &= ~0x20u;
    if (on)
        flags |= 0x20;
}
