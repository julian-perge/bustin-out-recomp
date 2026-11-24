struct S_00206BB0
{
    struct E
    {
        int a;
        int b;
        int c;
        int d;
    };
    E* data;
    E* FUN_00206bb0();
};

// 0x00206BB0
S_00206BB0::E* S_00206BB0::FUN_00206bb0()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
