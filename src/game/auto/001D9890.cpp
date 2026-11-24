struct S_001D9890
{
    char pad[0x20];
    unsigned flags;
    void FUN_001d9890(bool on);
};

// 0x001D9890
void S_001D9890::FUN_001d9890(bool on)
{
    flags &= ~0x2000;
    if (on)
        flags |= 0x2000;
}
