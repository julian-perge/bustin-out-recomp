struct S_001FF1C0
{
    int a;
    int b;
    S_001FF1C0* FUN_001ff1c0(const int* pa, const int* pb);
};

// 0x001FF1C0
S_001FF1C0* S_001FF1C0::FUN_001ff1c0(const int* pa, const int* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
