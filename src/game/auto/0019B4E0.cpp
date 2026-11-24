struct Elem_0019B4E0
{
    int a, b, c;
};

struct S_0019B4E0
{
    Elem_0019B4E0* p;
    Elem_0019B4E0* FUN_0019b4e0();
};

// 0x0019B4E0
Elem_0019B4E0* S_0019B4E0::FUN_0019b4e0()
{
    int n = p ? ((int*)p)[-1] : 0;
    return p + n;
}
