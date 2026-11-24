struct I_000f4da0
{
    virtual void FUN_v0();
    virtual void FUN_v1();
    virtual void FUN_v2();
};

struct S_000f4da0
{
    I_000f4da0* p;
    void FUN_000f4da0();
};

// 0x000F4DA0
void S_000f4da0::FUN_000f4da0()
{
    if (p) {
        p->FUN_v2();
        p = 0;
    }
}
