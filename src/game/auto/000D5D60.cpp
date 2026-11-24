struct P_000d5d60
{
    int a;
    int b;
};

struct S_000d5d60
{
    char pad0[8];
    unsigned flags;
    char pad[0xc];
    int a;
    int b;
    void FUN_000d5d60(const P_000d5d60* p);
};

// 0x000D5D60
void S_000d5d60::FUN_000d5d60(const P_000d5d60* p)
{
    a = p->a;
    int t = p->b;
    flags &= ~2u;
    b = t;
}
