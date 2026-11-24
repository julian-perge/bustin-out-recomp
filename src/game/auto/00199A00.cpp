struct S_00199A00
{
    char pad[0x5c];
    unsigned flags;
    void FUN_00199a00(bool on);
};

// 0x00199A00
void S_00199A00::FUN_00199a00(bool on)
{
    flags &= ~2u;
    if (on)
        flags |= 2;
}
