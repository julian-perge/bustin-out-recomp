struct S_001FDBB0
{
    struct E
    {
        int a;
        int b;
    };
    E* data;
    E* FUN_001fdbb0();
};

// 0x001FDBB0
S_001FDBB0::E* S_001FDBB0::FUN_001fdbb0()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
