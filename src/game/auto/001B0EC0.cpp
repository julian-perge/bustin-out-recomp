struct S_001B0EC0
{
    unsigned short a;
    int b;
    S_001B0EC0* FUN_001b0ec0(const unsigned short* pa, const int* pb);
};

// 0x001B0EC0
S_001B0EC0* S_001B0EC0::FUN_001b0ec0(const unsigned short* pa, const int* pb)
{
    a = *pa;
    b = *pb;
    return this;
}
