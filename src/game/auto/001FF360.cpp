struct S_001FF360
{
    int a;
    int b;
    S_001FF360* FUN_001ff360(const int* pa, const int* pb);
};

// 0x001FF360
S_001FF360* S_001FF360::FUN_001ff360(const int* pa, const int* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
