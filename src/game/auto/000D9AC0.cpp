struct S_000D9AC0_T
{
    char pad0[8];
    unsigned f8;
    char pad1[0x44];
    int v50;
    char pad2[7];
    unsigned char f5b;
};

struct S_000D9AC0
{
    char pad[0x5c];
    S_000D9AC0_T* t;
    void FUN_000d9ac0(int v);
};

// 0x000D9AC0
// parked: scheduling
void S_000D9AC0::FUN_000d9ac0(int v)
{
    S_000D9AC0_T* p = t;
    p->f5b |= 0x10;
    p->v50 = v;
    p->f8 |= 2;
}
