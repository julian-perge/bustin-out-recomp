struct E_001DB650
{
    int a, b, c;
};

struct S_001DB650
{
    E_001DB650* begin;
    E_001DB650* end;
    int FUN_001db650();
};

// 0x001DB650
int S_001DB650::FUN_001db650()
{
    return end - begin;
}
