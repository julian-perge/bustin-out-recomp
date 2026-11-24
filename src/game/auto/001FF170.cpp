struct S_001FF170
{
    int a;
    int b;
    S_001FF170* FUN_001ff170(const int* pa, const int* pb);
};

// 0x001FF170
S_001FF170* S_001FF170::FUN_001ff170(const int* pa, const int* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
