struct S_0021CAC0
{
    char a;
    char b;
    char c;
    int FUN_0021cac0();
};

// 0x0021CAC0
int S_0021CAC0::FUN_0021cac0()
{
    int n = 0;
    if (a != 0x7f)
        n = 1;
    if (c != 0x7f)
        n++;
    return n;
}
