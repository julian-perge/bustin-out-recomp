struct B_000E2290
{
    char pad0[8];
    int fl;
    char pad1[0x54 - 0xc];
    float f;
    char pad2[3];
    unsigned char g;
    void SetF(float v)
    {
        g |= 0x10;
        f = v;
    }
};

struct A_000E2290
{
    char pad[0x5c];
    B_000E2290* b;
};

struct S_000E2290
{
    char pad[0x64];
    A_000E2290* a;
    void FUN_000e2290(float v);
};

// The build moves the or of +0x8 before the store of +0x54; the original keeps source order. Helper and reorder forms did not change it.
// 0x000E2290
// parked: scheduling
void S_000E2290::FUN_000e2290(float v)
{
    B_000E2290* q = a->b;
    q->g |= 0x10;
    q->f = v;
    q->fl |= 2;
}
