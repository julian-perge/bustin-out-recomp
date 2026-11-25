struct S_002195D0
{
    char pad0[0x20];
    int a;
    char pad1[0x2b4 - 0x24];
    int b;
    bool f;
    int FUN_002195d0();
};

// 0x002195D0
int S_002195D0::FUN_002195d0()
{
    int d = a - b;
    if (d < 0)
    {
        if (f)
            d += 12;
        else
            d = 0;
    }
    return d;
}
