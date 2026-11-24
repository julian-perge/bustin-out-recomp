struct S_001FE6D0
{
    virtual void FUN_dummy0();
    virtual void FUN_dummy1();
    virtual void FUN_dummy2();
    virtual void FUN_dummy3();
    virtual void FUN_dummy4();
    virtual void FUN_dummy5();
    virtual void FUN_dummy6();
    virtual void FUN_dummy7();
    virtual void FUN_dummy8();
    virtual void FUN_dummy9();
    virtual void FUN_dummy10();
    virtual void FUN_dummy11();
    virtual void FUN_dummy12();
    virtual void FUN_dummy13();
    virtual void FUN_dummy14();
    virtual void FUN_dummy15();
    virtual void FUN_dummy16();
    virtual void FUN_dummy17();
    virtual void FUN_dummy18();
    virtual void FUN_dummy19();
    virtual void FUN_dummy20();
    virtual void FUN_slot21();
    char pad[0x10];
    int n;
    int FUN_001fe6d0();
};

// 0x001FE6D0
int S_001FE6D0::FUN_001fe6d0()
{
    if (n == 0)
        FUN_slot21();
    return ++n;
}
