struct S_001A59D0;

struct S_001A59D0_owner
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual int FUN_slot48(S_001A59D0* s);
};

struct S_001A59D0
{
    char pad0[0x30];
    S_001A59D0_owner* owner;
    char pad1[0xC];
    int cached;
    int FUN_001a59d0();
};

// 0x001A59D0
int S_001A59D0::FUN_001a59d0()
{
    if (cached == 0) {
        cached = owner->FUN_slot48(this);
    }
    return cached;
}
