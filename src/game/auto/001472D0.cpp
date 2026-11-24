struct S_001472D0Inner
{
    int pad;
    unsigned int n;
};

struct S_001472D0
{
    char pad[0x2c];
    S_001472D0Inner *p;
    char *FUN_001472d0();
};

// 0x001472D0
char *S_001472D0::FUN_001472d0()
{
    if (p)
        return (char *)p + (p->n >> 3);
    return 0;
}
