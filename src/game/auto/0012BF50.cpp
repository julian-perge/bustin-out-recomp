struct S_0012BF50
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void w(const void* p, int n);
};

// 0x0012BF50
S_0012BF50* FUN_0012bf50(S_0012BF50* s, int v)
{
    s->w(&v, 4);
    return s;
}
