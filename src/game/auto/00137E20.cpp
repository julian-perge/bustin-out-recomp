struct S_00137E20
{
    virtual void s0();
    virtual void s1();
    virtual void w(int v);
};

// 0x00137E20
S_00137E20* FUN_00137e20(S_00137E20* s, int* p)
{
    s->w(*p);
    return s;
}
