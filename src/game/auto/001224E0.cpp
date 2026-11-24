struct I_001224e0
{
    virtual void FUN_v0();
    virtual void FUN_v1(int);
    virtual void FUN_v2();
    virtual void FUN_v3();
};

struct S_001224e0
{
    int pad;
    int inner;
    void FUN_001224e0();
};

// 0x001224E0
void S_001224e0::FUN_001224e0()
{
    I_001224e0* i = (I_001224e0*)&inner;
    i->FUN_v1(-1);
    i->FUN_v3();
}
