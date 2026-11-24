struct S_00027B20_Elem
{
    int v[45];
};

struct S_00027B20
{
    S_00027B20_Elem* p;
    S_00027B20_Elem* FUN_00027b20(int n);
};

// 0x00027B20
S_00027B20_Elem* S_00027B20::FUN_00027b20(int n)
{
    return &p[n];
}
