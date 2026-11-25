struct V_000D6810
{
    int x, y;
};

struct I_000D6810
{
    char pad0[0xc];
    V_000D6810 vec;
    char pad1[0x3b - 0x14];
    unsigned char fl;
};

struct P_000D6810
{
    char pad[0x20];
    I_000D6810 in;
};

struct S_000D6810
{
    char pad[0x60];
    P_000D6810* p;
    void FUN_000d6810(V_000D6810* v);
};

// 0x000D6810
void S_000D6810::FUN_000d6810(V_000D6810* v)
{
    I_000D6810* q = &p->in;
    q->vec = *v;
    q->fl |= 0x10;
}
