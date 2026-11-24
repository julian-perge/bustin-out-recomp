struct S_0004A7E0_T
{
    virtual void FUN_0004a7e0_0();
    virtual void FUN_0004a7e0_1(int n);
};

struct S_0004A7E0
{
    S_0004A7E0_T* p;
    S_0004A7E0(S_0004A7E0_T* t);
};

// 0x0004A7E0
S_0004A7E0::S_0004A7E0(S_0004A7E0_T* t)
{
    p = t;
    t->FUN_0004a7e0_1(-1);
}
