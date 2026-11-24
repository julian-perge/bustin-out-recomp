struct S_001BFB30
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfb30(bool on);
};

// 0x001BFB30
void S_001BFB30::FUN_001bfb30(bool on)
{
    flags &= ~4u;
    if (on)
        flags |= 4;
}
