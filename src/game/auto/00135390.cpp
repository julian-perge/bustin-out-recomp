struct S_00135390
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void r(void* p, int n);
};

// 0x00135390
S_00135390* FUN_00135390(S_00135390* s, char* v)
{
    s->r(v, 1);
    return s;
}
