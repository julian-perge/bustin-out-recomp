struct S_001FF8E0
{
    int a;
    char b;
    S_001FF8E0* FUN_001ff8e0(const int* pa, const char* pb);
};

// 0x001FF8E0
S_001FF8E0* S_001FF8E0::FUN_001ff8e0(const int* pa, const char* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
