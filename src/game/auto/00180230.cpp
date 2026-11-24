struct S_00180230
{
    int a;
    int b;
    char c;
    S_00180230* FUN_00180230(char v);
};

// 0x00180230
S_00180230* S_00180230::FUN_00180230(char v)
{
    b = 0;
    a = 0;
    c = v;
    return this;
}
