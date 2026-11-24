struct T_001FE9D0
{
    virtual void v00();
    virtual void v01();
    virtual void v02();
    virtual void v03();
    virtual bool v04();
};

struct S_001FE9D0
{
    char pad[0xd8];
    T_001FE9D0* t;
    bool FUN_001fe9d0();
};

// 0x001FE9D0
bool S_001FE9D0::FUN_001fe9d0()
{
    if (t)
        return t->v04();
    return false;
}
