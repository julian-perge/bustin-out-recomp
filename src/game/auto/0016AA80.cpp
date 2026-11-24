struct S_0016AA80
{
    virtual void s0();
    virtual void s1();
    virtual void FUN_0016aa80s(int v);
};

struct S_0016AA80_b
{
    int v;
};

// 0x0016AA80
S_0016AA80* FUN_0016aa80(S_0016AA80* a, S_0016AA80_b* b)
{
    a->FUN_0016aa80s(b->v);
    return a;
}
