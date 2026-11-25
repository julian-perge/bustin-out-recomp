struct S_001C4330
{
    int a;
    int b;
    char c;
    char pad[0x13];
    int d;
    S_001C4330* FUN_001c4330(int x, char y);
};

// 0x001C4330
S_001C4330* S_001C4330::FUN_001c4330(int x, char y)
{
    a = x;
    b = 0;
    c = y;
    d = 0;
    return this;
}
