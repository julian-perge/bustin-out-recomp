struct S_00017C90;

struct S_00017C90_target
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void FUN_slot18(S_00017C90* from, int arg);
};

struct S_00017C90
{
    char pad[0x10];
    S_00017C90_target* target;
    void FUN_00017c90(int unused, int arg);
};

// 0x00017C90
void S_00017C90::FUN_00017c90(int unused, int arg)
{
    if (target) {
        target->FUN_slot18(this, arg);
    }
}
