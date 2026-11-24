struct S_0020F780
{
    struct E
    {
        int a;
        int b;
    };
    E* data;
    E* FUN_0020f780();
};

// 0x0020F780
S_0020F780::E* S_0020F780::FUN_0020f780()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
