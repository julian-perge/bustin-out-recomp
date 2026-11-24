struct S_00210690_Elem
{
    int v[11];
};

struct S_00210690
{
    S_00210690_Elem* p;
    S_00210690_Elem* FUN_00210690(int n);
};

// 0x00210690
S_00210690_Elem* S_00210690::FUN_00210690(int n)
{
    return &p[n];
}
