struct S_00049FF0_Obj
{
    virtual void FUN_s00();
    virtual void FUN_s01();
    virtual void FUN_s02();
    virtual void FUN_s03();
    virtual void FUN_s04(int a, int b);
};

// 0x00049FF0
S_00049FF0_Obj* FUN_00049ff0(S_00049FF0_Obj* p, int a)
{
    p->FUN_s04(a, 4);
    return p;
}
