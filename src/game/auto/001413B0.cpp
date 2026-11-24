struct S_001413B0
{
    int a;
    int b;
    char c;
    S_001413B0* FUN_001413b0(char v);
};

// 0x001413B0
S_001413B0* S_001413B0::FUN_001413b0(char v)
{
    b = 0;
    a = 0;
    c = v;
    return this;
}
