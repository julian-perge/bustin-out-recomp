struct S_00219580
{
    char pad0[0x1c];
    int a;
    char pad1[0x2b0 - 0x20];
    int b;
    char pad2[5];
    bool f;
    int FUN_00219580();
};

// 0x00219580
int S_00219580::FUN_00219580()
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
