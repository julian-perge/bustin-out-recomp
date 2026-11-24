struct S_001A4F10
{
    short* p;
    int n;
    S_001A4F10* FUN_001a4f10(short* a, int b);
};

// 0x001A4F10
S_001A4F10* S_001A4F10::FUN_001a4f10(short* a, int b)
{
    p = a;
    n = b;
    *a = 0;
    return this;
}
