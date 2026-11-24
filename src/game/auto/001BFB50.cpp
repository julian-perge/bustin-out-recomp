struct S_001BFB50
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfb50(bool on);
};

// 0x001BFB50
void S_001BFB50::FUN_001bfb50(bool on)
{
    flags &= ~0x8u;
    if (on)
        flags |= 0x8;
}
