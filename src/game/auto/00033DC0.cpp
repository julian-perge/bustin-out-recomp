struct R_00033DC0
{
    void* a;
    int b;
    int c;
    void Init(void* o, int cap, int cnt)
    {
        a = o;
        b = cap;
        c = cnt;
    }
};

struct S_00033DC0
{
    R_00033DC0* FUN_00033dc0(R_00033DC0* p);
};

// The original keeps ESI and EDI in use (an inlined initializer); direct stores and an Init helper build 23 bytes without them.
// 0x00033DC0
// parked: unclassified
R_00033DC0* S_00033DC0::FUN_00033dc0(R_00033DC0* p)
{
    p->Init(this, 0x40, 0);
    return p;
}
