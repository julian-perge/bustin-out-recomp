struct S_001FF190
{
    int a;
    char b;
    S_001FF190* FUN_001ff190(const int* pa, const char* pb);
};

// 0x001FF190
S_001FF190* S_001FF190::FUN_001ff190(const int* pa, const char* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
