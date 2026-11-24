struct S_00198930
{
    int n;
    int mask;
    void FUN_00198930(int bits);
};

// 0x00198930
void S_00198930::FUN_00198930(int bits)
{
    n = bits;
    mask = -1 << (bits - 1);
}
