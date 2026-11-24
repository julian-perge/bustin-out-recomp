struct S_000AFF70
{
    char pad[5];
    unsigned char f;
    int FUN_000aff70();
};

// 0x000AFF70
int S_000AFF70::FUN_000aff70()
{
    int r = 0;
    if (f & 1)
        r = 1;
    if (f & 0x10)
        r |= 2;
    return r;
}
