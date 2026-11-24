struct S_001F0800
{
    char pad[0x30];
    unsigned flags;
    void FUN_001f0800(bool on);
};

// 0x001F0800
void S_001F0800::FUN_001f0800(bool on)
{
    flags &= ~0x10u;
    if (on)
        flags |= 0x10;
}
