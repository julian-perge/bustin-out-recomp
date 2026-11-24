struct S_001C7C30
{
    char pad[0x48];
    unsigned flags;
    void FUN_001c7c30(bool on);
};

// 0x001C7C30
void S_001C7C30::FUN_001c7c30(bool on)
{
    flags &= ~0x40u;
    if (on)
        flags |= 0x40;
}
