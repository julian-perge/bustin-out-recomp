struct S_000716E0_Target
{
    virtual void FUN_s00();
    virtual void FUN_s01();
    virtual void FUN_s02();
    virtual void FUN_s03();
    virtual void FUN_s04();
    virtual void FUN_s05();
    virtual void FUN_s06(int a, int b);
};

struct S_000716E0
{
    char pad[0xbc];
    S_000716E0_Target* t;
    void FUN_000716e0(int a, int b);
};

// 0x000716E0
void S_000716E0::FUN_000716e0(int a, int b)
{
    if (t)
        t->FUN_s06(a, b);
}
