struct E_001B0E60
{
    char pad[20];
};

struct S_001B0E60
{
    E_001B0E60* b;
    E_001B0E60* e;
    int FUN_001b0e60();
};

// 0x001B0E60
int S_001B0E60::FUN_001b0e60()
{
    return e - b;
}
