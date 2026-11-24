struct P_000e2130
{
    int a;
    int b;
};

struct S_000e2130
{
    char pad0[20];
    int a;
    int b;
    char pad1[31];
    unsigned char fl;
    void FUN_000e2130(const P_000e2130* p);
};

// 0x000E2130
void S_000e2130::FUN_000e2130(const P_000e2130* p)
{
    a = p->a;
    b = p->b;
    fl |= 0x10;
}
