struct S_00152110
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void w(const void* p, int n);
};

// 0x00152110
S_00152110* FUN_00152110(S_00152110* s, bool v)
{
    s->w(&v, 1);
    return s;
}
