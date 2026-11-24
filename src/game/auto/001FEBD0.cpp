struct T_001FEBD0
{
    virtual void v00();
    virtual void v01();
    virtual void v02();
    virtual void v03();
    virtual bool v04();
};

struct S_001FEBD0
{
    char pad[0xc0];
    T_001FEBD0* t;
    bool FUN_001febd0();
};

// 0x001FEBD0
bool S_001FEBD0::FUN_001febd0()
{
    if (t)
        return t->v04();
    return false;
}
