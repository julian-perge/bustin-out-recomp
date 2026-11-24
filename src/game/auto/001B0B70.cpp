struct S_001B0B70
{
    short a;
    int b;
    S_001B0B70* FUN_001b0b70(short x, int y);
};

// 0x001B0B70
S_001B0B70* S_001B0B70::FUN_001b0b70(short x, int y)
{
    a = x;
    b = y;
    return this;
}
