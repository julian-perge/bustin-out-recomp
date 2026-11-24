struct S_00049FD0_Obj
{
    virtual void FUN_s00();
    virtual void FUN_s01();
    virtual void FUN_s02();
    virtual void FUN_s03();
    virtual void FUN_s04(int a, int b);
};

// 0x00049FD0
S_00049FD0_Obj* FUN_00049fd0(S_00049FD0_Obj* p, int a)
{
    p->FUN_s04(a, 1);
    return p;
}
