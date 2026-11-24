struct S_0012A140
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void FUN_0012a140_slot(int a);
    char pad[0x78];
    float f;
    void FUN_0012a140(int a, float x);
};

// 0x0012A140
void S_0012A140::FUN_0012a140(int a, float x)
{
    f = x;
    FUN_0012a140_slot(a);
}
