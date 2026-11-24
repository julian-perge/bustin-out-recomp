struct S_00207D20
{
    struct E
    {
        int a;
        int b;
    };
    E* data;
    E* FUN_00207d20();
};

// 0x00207D20
S_00207D20::E* S_00207D20::FUN_00207d20()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
