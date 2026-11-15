struct Link_0007EBB0
{
    Link_0007EBB0* next;
};

struct S_0007EBB0
{
    Link_0007EBB0* head;
    void fn_0007EBB0(Link_0007EBB0* n);
    void fn_0007FF50(Link_0007EBB0* n);
};

// 0x0007EBB0
void S_0007EBB0::fn_0007EBB0(Link_0007EBB0* n)
{
    if (n) {
        n->next = head;
        head = n;
    }
}

// 0x0007FF50
void S_0007EBB0::fn_0007FF50(Link_0007EBB0* n)
{
    if (n) {
        n->next = head;
        head = n;
    }
}

struct S_000814F0
{
    int a;
    int b;
    int c;
    char flag;
    S_000814F0* fn_000814F0();
};

// 0x000814F0
S_000814F0* S_000814F0::fn_000814F0()
{
    c = 0;
    b = 0;
    flag = 1;
    a = 0;
    return this;
}

struct S_00081550
{
    char pad[0x30];
    int b;
    int pad2;
    int a;
    void fn_00081550(int x, int y);
};

// 0x00081550
void S_00081550::fn_00081550(int x, int y)
{
    a = x;
    b = y;
}

// 0x00082B80
void fn_00082B80(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_00086CD0
{
    int a;
    int b;
    char flag;
    int c;
    S_00086CD0* fn_00086CD0();
};

// 0x00086CD0
S_00086CD0* S_00086CD0::fn_00086CD0()
{
    b = 0;
    a = 0;
    flag = 1;
    c = 0;
    return this;
}

struct Sub_0008C760
{
    virtual void v0();
    virtual void v1();
    virtual void v2(int a);
};

struct S_0008C760
{
    char pad[0x60];
    Sub_0008C760* sub;
    void fn_0008C760(int a);
};

// 0x0008C760
void S_0008C760::fn_0008C760(int a)
{
    if (sub)
        sub->v2(a);
}
