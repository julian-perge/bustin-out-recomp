struct T_000F5070
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void FUN_000f5070_5(int a);
};

struct S_000F5070
{
    char pad0[0x30];
    T_000F5070* t;
    char pad1[0x80 - 0x34];
    char on;
    void FUN_000f5070(int a);
};

// 0x000F5070
void S_000F5070::FUN_000f5070(int a)
{
    if (on) {
        T_000F5070* p = t;
        if (p)
            p->FUN_000f5070_5(a);
    }
}
