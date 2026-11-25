struct S_001AF340_elem
{
    char b[36];
};

struct S_001AF340
{
    int FUN_001af340();
};

// 0x001AF340
int S_001AF340::FUN_001af340()
{
    S_001AF340_elem* const* base = (S_001AF340_elem* const*)((char*)this - 0x64);
    return (base[1] - base[0]) - 1;
}
