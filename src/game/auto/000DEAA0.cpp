struct S_000DEAA0
{
    char pad[0xb];
    unsigned char f;
    void FUN_000deaa0(bool b);
};

// 0x000DEAA0
void S_000DEAA0::FUN_000deaa0(bool b)
{
    if (b)
        f |= 0x1;
    else
        f &= ~0x1;
}
