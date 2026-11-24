struct S_00198990
{
    int pad;
    int m;
    void FUN_00198990(int* p);
};

// 0x00198990
void S_00198990::FUN_00198990(int* p)
{
    if (m & *p)
        *p |= m;
}
