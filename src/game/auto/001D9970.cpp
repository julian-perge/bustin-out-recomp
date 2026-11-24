struct S_001D9970
{
    char pad[0x48];
    unsigned flags;
    void FUN_001d9970(bool on);
};

// 0x001D9970
void S_001D9970::FUN_001d9970(bool on)
{
    flags &= ~0x100;
    if (on)
        flags |= 0x100;
}
