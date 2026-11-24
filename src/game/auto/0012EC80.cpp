struct S_0012EC80
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void w(const void* p, int n);
};

// 0x0012EC80
S_0012EC80* FUN_0012ec80(S_0012EC80* s, unsigned int v)
{
    s->w(&v, 4);
    return s;
}
