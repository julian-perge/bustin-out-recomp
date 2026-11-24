struct S_001A59F0Cb
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
    virtual void FUN_x(int a);
};

struct S_001A59F0Inner
{
    char pad[0x8c];
    int val;
};

struct S_001A59F0
{
    char pad[0x18];
    S_001A59F0Inner *inner;
    char pad2[0x30 - 0x1c];
    S_001A59F0Cb *cb;
    void FUN_001a59f0();
};

// 0x001A59F0
void S_001A59F0::FUN_001a59f0()
{
    cb->FUN_x(inner->val);
}
