struct S_000D72B0
{
    char pad[0x8];
    unsigned f;
    void FUN_000d72b0(bool b);
};

// 0x000D72B0
void S_000D72B0::FUN_000d72b0(bool b)
{
    if (b)
        f |= 0x1;
    else
        f &= ~0x1;
}
