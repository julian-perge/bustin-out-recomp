struct S_0005A9F0_T
{
    virtual void FUN_0005a9f0_0();
    virtual void FUN_0005a9f0_1();
};

struct S_0005A9F0
{
    S_0005A9F0_T* p;
    void FUN_0005a9f0();
};

// 0x0005A9F0
void S_0005A9F0::FUN_0005a9f0()
{
    if (p)
        p->FUN_0005a9f0_1();
    p = 0;
}
