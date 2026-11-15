struct A_000FAE60
{
};

struct S_000FAE60
{
    int a, b, c;
    S_000FAE60* FUN_000FAE60(const A_000FAE60& alloc);
    S_000FAE60* FUN_000FAED0();
};

// 0x000FAED0
S_000FAE60* S_000FAE60::FUN_000FAED0()
{
    A_000FAE60 tmp;
    return FUN_000FAE60(tmp);
}
