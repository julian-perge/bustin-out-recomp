struct S_00207D40
{
    struct E
    {
        int a;
        int b;
    };
    E* data;
    E* FUN_00207d40();
};

// 0x00207D40
S_00207D40::E* S_00207D40::FUN_00207d40()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
