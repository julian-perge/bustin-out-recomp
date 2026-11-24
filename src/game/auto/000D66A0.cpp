struct P_000d66a0
{
    int a;
    int b;
};

struct S_000d66a0
{
    char pad0[44];
    int a;
    int b;
    char pad1[39];
    unsigned char fl;
    void FUN_000d66a0(const P_000d66a0* p);
};

// 0x000D66A0
void S_000d66a0::FUN_000d66a0(const P_000d66a0* p)
{
    a = p->a;
    b = p->b;
    fl |= 0x10;
}
