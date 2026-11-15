// 0x0004AB30
void fn_0004AB30(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x0004AB50
void fn_0004AB50(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_0004CE80
{
    char pad[0x64];
    int b;
    int a;
    void fn_0004CE80(int x);
};

// 0x0004CE80
void S_0004CE80::fn_0004CE80(int x)
{
    a = x;
    b = 0;
}

struct Sub_0004D250
{
    virtual void v0();
    virtual void v1();
    virtual void v2(int a);
};

struct S_0004D250
{
    char pad[0x14];
    Sub_0004D250* sub;
    void fn_0004D250(int a);
};

// 0x0004D250
void S_0004D250::fn_0004D250(int a)
{
    if (sub)
        sub->v2(a);
}
