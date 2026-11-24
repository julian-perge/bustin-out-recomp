struct S_000D5E50
{
    char pad[0x58];
    unsigned f;
    void FUN_000d5e50(bool b);
};

// 0x000D5E50
void S_000D5E50::FUN_000d5e50(bool b)
{
    if (b)
        f |= 0x20;
    else
        f &= ~0x20;
}
