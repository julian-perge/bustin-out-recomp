struct E_001DB4E0
{
    int a, b, c;
};

struct S_001DB4E0
{
    E_001DB4E0* begin;
    E_001DB4E0* end;
    int FUN_001db4e0();
};

// 0x001DB4E0
int S_001DB4E0::FUN_001db4e0()
{
    return end - begin;
}
