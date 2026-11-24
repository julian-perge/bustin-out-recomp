struct S_0021D9A0
{
    virtual void s0();
    virtual void s1();
    virtual int FUN_0021D9A0_slot(int a, int b);
    bool FUN_0021D9A0(int a, int b);
};

// 0x0021D9A0
bool S_0021D9A0::FUN_0021D9A0(int a, int b)
{
    bool r = FUN_0021D9A0_slot(a, b) == b;
    return r;
}
