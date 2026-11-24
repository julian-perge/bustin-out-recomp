struct S_001F0740
{
    char pad[0x30];
    unsigned flags;
    void FUN_001f0740(bool on);
};

// 0x001F0740
void S_001F0740::FUN_001f0740(bool on)
{
    flags &= ~0x1u;
    if (on)
        flags |= 0x1;
}
