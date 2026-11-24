struct S_001F07A0
{
    char pad[0x30];
    unsigned flags;
    void FUN_001f07a0(bool on);
};

// 0x001F07A0
void S_001F07A0::FUN_001f07a0(bool on)
{
    flags &= ~0x4u;
    if (on)
        flags |= 0x4;
}
