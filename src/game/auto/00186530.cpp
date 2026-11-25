struct S_00186530
{
    char pad0[4];
    int a, b;
    char pad[0x1C - 0x0C];
    int c;
    bool FUN_00186530(int x, int y, int z);
};

// 0x00186530
bool S_00186530::FUN_00186530(int x, int y, int z)
{
    a = x;
    b = y;
    c = z;
    return true;
}
