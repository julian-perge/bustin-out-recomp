struct S_00205DE0
{
    int a;
    char b;
    S_00205DE0* FUN_00205de0(const int* pa, const char* pb);
};

// 0x00205DE0
S_00205DE0* S_00205DE0::FUN_00205de0(const int* pa, const char* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
