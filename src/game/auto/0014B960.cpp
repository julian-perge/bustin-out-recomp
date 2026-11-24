struct S_0014B960_Src
{
    int d[7];
};

struct S_0014B960
{
    char pad[0x80];
    S_0014B960_Src s;
    void FUN_0014b960(const S_0014B960_Src* p);
};

// 0x0014B960
void S_0014B960::FUN_0014b960(const S_0014B960_Src* p)
{
    s = *p;
}
