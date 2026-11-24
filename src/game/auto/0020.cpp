// 0x0020D800
void fn_0020D800(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x0020D950
void fn_0020D950(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_0020FD40Inner
{
    short* p;
    short size();
};

short S_0020FD40Inner::size()
{
    if (p)
        return p[-2];
    return 0;
}

struct S_0020FD40
{
    char pad[8];
    S_0020FD40Inner* inner;
    short fn_0020FD40();
};

// 0x0020FD40
short S_0020FD40::fn_0020FD40()
{
    return inner->size();
}

struct S_002008F0
{
    S_002008F0* FUN_002008F0(int k);
};

// 0x002008F0
S_002008F0* S_002008F0::FUN_002008F0(int k)
{
    if (k == 0x12)
        return this;
    return 0;
}

struct Obj_0020F4E0
{
    virtual void v0();
    virtual void v1();
    virtual int FUN_Slot2(int a);
};
struct S_0020F4E0
{
    char pad[8];
    Obj_0020F4E0* p;
    int FUN_0020F4E0();
};

// 0x0020F4E0
int S_0020F4E0::FUN_0020F4E0()
{
    Obj_0020F4E0* q = p;
    if (q)
        return q->FUN_Slot2(-1);
    return 0;
}
