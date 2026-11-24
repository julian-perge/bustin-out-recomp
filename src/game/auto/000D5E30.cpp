struct S_000D5E30
{
    char pad[0x58];
    unsigned f;
    void FUN_000d5e30(bool b);
};

// 0x000D5E30
void S_000D5E30::FUN_000d5e30(bool b)
{
    if (b)
        f |= 0x8;
    else
        f &= ~0x8;
}
