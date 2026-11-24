struct E_001DB470
{
    char pad[160];
};

struct S_001DB470
{
    E_001DB470* b;
    E_001DB470* e;
    int FUN_001db470();
};

// 0x001DB470
int S_001DB470::FUN_001db470()
{
    return e - b;
}
