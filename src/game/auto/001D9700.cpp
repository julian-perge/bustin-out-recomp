struct S_001D9700_A
{
    virtual void a0();
    int p;
    int q;
    int m1;
};

struct S_001D9700_C
{
    int c[7];
};

struct S_001D9700_B : S_001D9700_C, virtual S_001D9700_A
{
    virtual void b0();
};

struct S_001D9700 : virtual S_001D9700_B
{
    virtual void d0();
    void FUN_001D9700(int x);
};

// 0x001D9700
// parked: source shape
void S_001D9700::FUN_001D9700(int x)
{
    q = x;
}
