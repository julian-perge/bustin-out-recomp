struct S_0020FDB0
{
    struct E
    {
        int a;
        int b;
    };
    E* data;
    E* FUN_0020fdb0();
};

// 0x0020FDB0
S_0020FDB0::E* S_0020FDB0::FUN_0020fdb0()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
