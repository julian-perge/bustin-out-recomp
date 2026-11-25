struct E_000A0D30
{
    int a;
    int b;
    int c;
};

struct S_000A0D30
{
    E_000A0D30* p;
    E_000A0D30* FUN_000a0d30();
};

// 0x000A0D30
E_000A0D30* S_000A0D30::FUN_000a0d30()
{
    int n = p ? ((int*)p)[-1] : 0;
    return p + n;
}
