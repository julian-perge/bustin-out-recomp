struct S_000D5C40
{
    char pad[0x38];
    unsigned f;
    void FUN_000d5c40(bool b);
};

// 0x000D5C40
void S_000D5C40::FUN_000d5c40(bool b)
{
    if (b)
        f |= 0x20;
    else
        f &= ~0x20;
}
