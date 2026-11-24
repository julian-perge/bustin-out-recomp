struct S_00180250
{
    int a;
    int b;
    char c;
    S_00180250* FUN_00180250(char v);
};

// 0x00180250
S_00180250* S_00180250::FUN_00180250(char v)
{
    b = 0;
    a = 0;
    c = v;
    return this;
}
