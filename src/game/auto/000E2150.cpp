struct P_000e2150
{
    int a;
    int b;
};

struct S_000e2150
{
    char pad0[52];
    int a;
    int b;
    char pad1[31];
    unsigned char fl;
    void FUN_000e2150(const P_000e2150* p);
};

// 0x000E2150
void S_000e2150::FUN_000e2150(const P_000e2150* p)
{
    a = p->a;
    b = p->b;
    fl |= 0x10;
}
