struct S_00168ED0
{
    int a;
    int b;
    char c;
    S_00168ED0* FUN_00168ed0(char v);
};

// 0x00168ED0
S_00168ED0* S_00168ED0::FUN_00168ed0(char v)
{
    b = 0;
    a = 0;
    c = v;
    return this;
}
