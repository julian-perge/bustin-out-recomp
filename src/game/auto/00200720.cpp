struct S_00200720
{
    int a;
    char b;
    S_00200720* FUN_00200720(const int* pa, const char* pb);
};

// 0x00200720
S_00200720* S_00200720::FUN_00200720(const int* pa, const char* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
