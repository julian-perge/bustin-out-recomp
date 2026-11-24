// 0x00011BB0
const unsigned* fn_00011BB0(const unsigned* a, const unsigned* b)
{
    if (*a < *b)
        a = b;
    return a;
}

// 0x00011BD0
void fn_00011BD0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x00013730
int fn_00013730(char a)
{
    if (a)
        return 0;
    __debugbreak();
    return 1;
}

// 0x00013C40
float fn_00013C40(float t, float a, float b)
{
    return (b - a) * t + a;
}

struct S_0001BB80
{
    char pad0[0x45a1];
    char flag;
    char pad1[0x523c - 0x45a2];
    char out;
    void fn_0001BB80();
};

// 0x0001BB80
void S_0001BB80::fn_0001BB80()
{
    if (!flag)
        out = 1;
}

struct S_00017C70
{
    char pad[0x24];
    int a;
    int pad2;
    int b;
    void fn_00017C70(const int* p);
};

// 0x00017C70
void S_00017C70::fn_00017C70(const int* p)
{
    a = p[0];
    b = p[1];
}

struct S_00018120Inner
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
};

struct S_00018120
{
    char pad0[4];
    S_00018120Inner* inner;
    char pad8[4];
    char flag;
    void fn_00018120();
};
// 0x00018120
void S_00018120::fn_00018120()
{
    if (!flag)
        flag = 1;
    inner->v2();
}

struct S_00013C90
{
    int a;
    int b;
    S_00013C90(const S_00013C90& o);
};

// 0x00013C90
S_00013C90::S_00013C90(const S_00013C90& o)
{
    a = o.a;
    b = o.b;
}

struct S_00018500
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual void v18();
    virtual void v19();
    virtual void FUN_Refresh();
    char pad[0x70 - 4];
    int f70;
    int f74;
    float f78;
    float f7c;
    void FUN_00018500(float v);
    void FUN_00018520(float v);
};

// 0x00018500
void S_00018500::FUN_00018500(float v)
{
    f78 = v;
    FUN_Refresh();
}

// 0x00018520
void S_00018500::FUN_00018520(float v)
{
    f7c = v;
    FUN_Refresh();
}
