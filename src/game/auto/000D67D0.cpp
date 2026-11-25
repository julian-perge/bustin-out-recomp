struct P_000D67D0
{
    int pad0;
    int pad4;
    int fl;
    char pad[0x48];
    float v;
    char pad2[3];
    unsigned char fb;
};

struct S_000D67D0
{
    char pad[92];
    P_000D67D0* p;
    void FUN_000d67d0(float x);
};

// 0x000D67D0
// parked: scheduling
void S_000D67D0::FUN_000d67d0(float x)
{
    P_000D67D0* q = p;
    q->fb |= 0x10;
    q->v = x;
    q->fl |= 2;
}
