struct S_00143690
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void r(void* p, int n);
};

// 0x00143690
S_00143690* FUN_00143690(S_00143690* s, short* v)
{
    s->r(v, 2);
    return s;
}
