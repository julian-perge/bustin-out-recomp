struct S_0012A0F0
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void FUN_0012a0f0_5(int a);
    char pad[0x78 - 4];
    float f;
    void FUN_0012a0f0(int a, float x);
};

// 0x0012A0F0
void S_0012A0F0::FUN_0012a0f0(int a, float x)
{
    f = x;
    FUN_0012a0f0_5(a);
}
