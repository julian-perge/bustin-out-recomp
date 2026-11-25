struct S_0005D630
{
    char pad[0x1C];
    unsigned flags;
    void FUN_0005D630(char on);
};

// 0x0005D630
void S_0005D630::FUN_0005D630(char on)
{
    flags = on ? (flags | 1) : (flags & ~1u);
}
