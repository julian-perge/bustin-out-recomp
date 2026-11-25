struct V_000E2210
{
    int x, y;
};

struct I_000E2210
{
    char pad0[0x14];
    V_000E2210 vec;
    char pad1[0x3b - 0x1c];
    unsigned char fl;
};

struct P_000E2210
{
    char pad[0x20];
    I_000E2210 in;
};

struct S_000E2210
{
    char pad[0x60];
    P_000E2210* p;
    void FUN_000e2210(V_000E2210* v);
};

// 0x000E2210
void S_000E2210::FUN_000e2210(V_000E2210* v)
{
    I_000E2210* q = &p->in;
    q->vec = *v;
    q->fl |= 0x10;
}
