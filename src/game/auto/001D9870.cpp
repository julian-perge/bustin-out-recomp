struct S_001D9870
{
    char pad[0x20];
    unsigned flags;
    void FUN_001d9870(bool on);
};

// 0x001D9870
void S_001D9870::FUN_001d9870(bool on)
{
    flags &= ~0x800;
    if (on)
        flags |= 0x800;
}
