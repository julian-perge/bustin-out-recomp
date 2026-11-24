struct S_000DEA00
{
    char pad[0x38];
    unsigned f;
    void FUN_000dea00(bool b);
};

// 0x000DEA00
void S_000DEA00::FUN_000dea00(bool b)
{
    if (b)
        f |= 0x10;
    else
        f &= ~0x10;
}
