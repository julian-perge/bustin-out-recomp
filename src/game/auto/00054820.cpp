struct S_00054820
{
    char pad0[8];
    char flag;
    char pad1[0x23];
    int b;
    char pad2[0xc];
    int a;
    void FUN_00054820(int x, int y);
};

// 0x00054820
void S_00054820::FUN_00054820(int x, int y)
{
    a = x;
    b = y;
    if (!flag) {
        flag = 1;
    }
}
