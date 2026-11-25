struct S_001FD700
{
    int a;
    int b;
    short c;
    S_001FD700* FUN_001fd700(int x, short y);
};

// 0x001FD700
S_001FD700* S_001FD700::FUN_001fd700(int x, short y)
{
    a = x;
    b = 0;
    c = y;
    return this;
}
