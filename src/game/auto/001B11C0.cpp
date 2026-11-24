struct Elem12
{
    char a, b, c;
};

struct S_001B11C0
{
    Elem12* first;
    Elem12* last;
    Elem12* end;
    int FUN_001b11c0();
};

// 0x001B11C0
int S_001B11C0::FUN_001b11c0()
{
    return end - first;
}
