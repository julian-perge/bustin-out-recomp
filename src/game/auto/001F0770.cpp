struct S_001F0770
{
    char pad[0x30];
    unsigned flags;
    void FUN_001f0770(bool on);
};

// 0x001F0770
void S_001F0770::FUN_001f0770(bool on)
{
    flags &= ~0x2u;
    if (on)
        flags |= 0x2;
}
