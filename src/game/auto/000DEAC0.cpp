struct S_000DEAC0
{
    char pad[0xb];
    unsigned char f;
    void FUN_000deac0(bool b);
};

// 0x000DEAC0
void S_000DEAC0::FUN_000deac0(bool b)
{
    if (b)
        f |= 0x02;
    else
        f &= ~0x02;
}
