struct S_001F2960
{
    int a;
    int b;
    S_001F2960* FUN_001f2960(const int* p, const int* q);
};

// 0x001F2960
S_001F2960* S_001F2960::FUN_001f2960(const int* p, const int* q)
{
    a = *p;
    b = *q;
    return this;
}
