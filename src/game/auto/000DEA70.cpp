struct S_000DEA70
{
    char pad[0xa];
    unsigned char f;
    void FUN_000dea70(bool b);
};

// 0x000DEA70
void S_000DEA70::FUN_000dea70(bool b)
{
    if (b)
        f |= 0x80;
    else
        f &= ~0x80;
}
