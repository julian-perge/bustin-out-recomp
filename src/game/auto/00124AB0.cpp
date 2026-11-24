struct S_00124AB0
{
    int d[64];
    int FUN_00124AB0(int a, int b);
};

// 0x00124AB0
int S_00124AB0::FUN_00124AB0(int a, int b)
{
    return d[b + a * 2 + 0x16];
}
