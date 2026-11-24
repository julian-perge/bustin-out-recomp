struct S_001C1010_elem
{
    int v[3];
};

struct S_001C1010
{
    S_001C1010_elem* p;
    S_001C1010_elem* FUN_001C1010();
};

// 0x001C1010
S_001C1010_elem* S_001C1010::FUN_001C1010()
{
    int n = p ? ((int*)p)[-1] : 0;
    return p + n;
}
