struct VBase_00071A00
{
    virtual void v00();
    virtual void v01();
    virtual void v02();
    virtual void v03();
    virtual void v04();
    virtual void v05();
    virtual void v06();
    virtual void v07();
    virtual void v08();
    virtual void v09();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual int FUN_00071A00();
};

struct Pre_00071A00
{
    char pad[0x20];
};

struct S_00071A00 : Pre_00071A00, virtual VBase_00071A00
{
};

// 0x00071A00
int FUN_00071a00(S_00071A00* p)
{
    if (p)
        return p->FUN_00071A00();
    return 0;
}
