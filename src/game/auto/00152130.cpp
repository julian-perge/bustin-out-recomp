struct S_00152130
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void w(const void* p, int n);
};

// 0x00152130
S_00152130* FUN_00152130(S_00152130* s, short v)
{
    s->w(&v, 2);
    return s;
}
