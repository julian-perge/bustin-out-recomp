struct S_00036A00_target
{
    virtual void FUN_0();
    virtual void FUN_1();
    virtual void FUN_2();
    virtual void FUN_3();
    virtual void FUN_4();
    virtual void FUN_5();
    virtual void FUN_6();
    virtual int FUN_7();
};

struct S_00036A00
{
    char pad[0x10c];
    S_00036A00_target* t;
    int FUN_00036a00();
};

// 0x00036A00
int S_00036A00::FUN_00036a00()
{
    if (t)
        return t->FUN_7();
    return 0;
}
