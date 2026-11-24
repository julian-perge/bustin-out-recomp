struct T_001FEA50
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
};

struct S_001FEA50
{
    char pad[0xc8];
    int n;
    char pad2[0xc];
    T_001FEA50* t;
    bool FUN_001fea50();
};

// 0x001FEA50
bool S_001FEA50::FUN_001fea50()
{
    if (--n == 0)
        t->v09();
    return true;
}
