struct S_001520F0
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void w(const void* p, int n);
};

// 0x001520F0
S_001520F0* FUN_001520f0(S_001520F0* s, char v)
{
    s->w(&v, 1);
    return s;
}
