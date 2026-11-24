struct S_000D5C20
{
    char pad[0x38];
    unsigned f;
    void FUN_000d5c20(bool b);
};

// 0x000D5C20
void S_000D5C20::FUN_000d5c20(bool b)
{
    if (b)
        f |= 0x8;
    else
        f &= ~0x8;
}
