struct S_00198BE0
{
    char pad0[8];
    int a;
    int b;
    char pad1[3];
    char flag;
    char pad2[0x20 - 0x14];
    int c;
    int d;
    void FUN_00198BE0();
};

// 0x00198BE0
void S_00198BE0::FUN_00198BE0()
{
    if (flag)
        c = 0;
    if (b == 0)
        a = d;
}
