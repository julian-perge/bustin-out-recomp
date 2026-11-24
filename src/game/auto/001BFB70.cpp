struct S_001BFB70
{
    char pad[0x48];
    unsigned flags;
    void FUN_001bfb70(bool on);
};

// 0x001BFB70
void S_001BFB70::FUN_001bfb70(bool on)
{
    flags &= ~0x10u;
    if (on)
        flags |= 0x10;
}
