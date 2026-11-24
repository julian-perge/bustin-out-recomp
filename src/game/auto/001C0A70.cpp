struct S_001C0A70
{
    char pad[8];
    int** p;
    int FUN_001c0a70(int unused);
};

// 0x001C0A70
int S_001C0A70::FUN_001c0a70(int unused)
{
    if (p && *p)
        return (*p)[-1];
    return 0;
}
