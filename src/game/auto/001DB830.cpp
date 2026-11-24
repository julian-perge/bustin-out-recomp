struct E_001DB830
{
    int a, b, c;
};

struct S_001DB830
{
    E_001DB830* begin;
    int pad;
    E_001DB830* end;
    int FUN_001db830();
};

// 0x001DB830
int S_001DB830::FUN_001db830()
{
    return end - begin;
}
