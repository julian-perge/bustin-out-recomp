struct S_000D5DF0
{
    char pad[0x8];
    unsigned f;
    void FUN_000d5df0(bool b);
};

// 0x000D5DF0
void S_000D5DF0::FUN_000d5df0(bool b)
{
    if (b)
        f |= 0x8;
    else
        f &= ~0x8;
}
