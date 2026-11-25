struct S_0016B5B0_B
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual bool FUN_0016b5b0_s4();
};

struct S_0016B5B0
{
    char pad[0x30];
    S_0016B5B0_B* p;
    int FUN_0016b5b0();
};

// 0x0016B5B0
int S_0016B5B0::FUN_0016b5b0()
{
    if (p && !p->FUN_0016b5b0_s4()) {
        return false;
    }
    return true;
}
