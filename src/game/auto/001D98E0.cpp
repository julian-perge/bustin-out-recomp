struct S_001D98E0
{
    char pad[0x20];
    unsigned flags;
    void FUN_001d98e0(bool on);
};

// 0x001D98E0
void S_001D98E0::FUN_001d98e0(bool on)
{
    flags &= ~0x8000;
    if (on)
        flags |= 0x8000;
}
