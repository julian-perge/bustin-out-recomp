struct S_001B52F0_A
{
    virtual void a0();
    int p;
    int q;
    int m1;
};

struct S_001B52F0_C
{
    int c[7];
};

struct S_001B52F0_B : S_001B52F0_C, virtual S_001B52F0_A
{
    virtual void b0();
};

struct S_001B52F0 : virtual S_001B52F0_B
{
    virtual void d0();
    void FUN_001B52F0(int x);
};

// 0x001B52F0
// parked: source shape
void S_001B52F0::FUN_001B52F0(int x)
{
    m1 = x;
}
