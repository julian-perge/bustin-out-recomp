struct S_000D5E10
{
    char pad[0x8];
    unsigned f;
    void FUN_000d5e10(bool b);
};

// 0x000D5E10
void S_000D5E10::FUN_000d5e10(bool b)
{
    if (b)
        f |= 0x2;
    else
        f &= ~0x2;
}
