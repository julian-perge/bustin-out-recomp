struct S_001F07D0
{
    char pad[0x30];
    unsigned flags;
    void FUN_001f07d0(bool on);
};

// 0x001F07D0
void S_001F07D0::FUN_001f07d0(bool on)
{
    flags &= ~0x8u;
    if (!on)
        flags |= 0x8;
}
