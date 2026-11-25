struct S_0016AAA0_A
{
    int a;
    int b;
};

struct S_0016AAA0
{
    virtual void FUN_0016aaa0_s0();
    virtual void FUN_0016aaa0_s1(int a, int b);
};

// 0x0016AAA0
S_0016AAA0* FUN_0016aaa0(S_0016AAA0* p, S_0016AAA0_A* s)
{
    p->FUN_0016aaa0_s1(s->a, s->b);
    return p;
}
