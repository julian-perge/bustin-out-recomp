struct S_001D98B0
{
    char pad[0x20];
    unsigned flags;
    void FUN_001d98b0(bool on);
};

// 0x001D98B0
void S_001D98B0::FUN_001d98b0(bool on)
{
    flags &= ~0x4000;
    if (on)
        flags |= 0x4000;
}
