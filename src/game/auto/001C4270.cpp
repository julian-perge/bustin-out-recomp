struct S_001C4270
{
    char pad[0x48];
    unsigned flags;
    void FUN_001c4270(bool on);
};

// 0x001C4270
void S_001C4270::FUN_001c4270(bool on)
{
    flags &= ~0x200;
    if (on)
        flags |= 0x200;
}
