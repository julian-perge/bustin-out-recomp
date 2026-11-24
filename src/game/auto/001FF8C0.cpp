struct S_001FF8C0
{
    int a;
    char b;
    S_001FF8C0* FUN_001ff8c0(const int* pa, const char* pb);
};

// 0x001FF8C0
S_001FF8C0* S_001FF8C0::FUN_001ff8c0(const int* pa, const char* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
