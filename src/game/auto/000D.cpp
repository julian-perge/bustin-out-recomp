// 0x000D6570
void fn_000D6570(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct Inner_000D9820
{
    char pad[0xc];
    float v;
};

struct S_000D9820
{
    char pad[0x44];
    Inner_000D9820* inner;
    void fn_000D9820(float x);
};

// 0x000D9820
void S_000D9820::fn_000D9820(float x)
{
    inner->v = x;
}

// 0x000DF880
void fn_000DF880(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_000D5CF0Arg
{
    int x;
    int y;
};

struct S_000D5CF0
{
    char pad[0x10];
    int a;
    int b;
    void fn_000D5CF0(const S_000D5CF0Arg* v);
};
// 0x000D5CF0
void S_000D5CF0::fn_000D5CF0(const S_000D5CF0Arg* v)
{
    a = v->x;
    b = v->y;
}

struct S_000D5FF0Arg
{
    int x;
    int y;
};

struct S_000D5FF0
{
    char pad[0x74];
    int a;
    int b;
    void fn_000D5FF0(const S_000D5FF0Arg* v);
};
// 0x000D5FF0
void S_000D5FF0::fn_000D5FF0(const S_000D5FF0Arg* v)
{
    a = v->x;
    b = v->y;
}

struct S_000D9890Arg
{
    int x;
    int y;
};

struct S_000D9890
{
    char pad[0x24];
    int a;
    int b;
    void fn_000D9890(const S_000D9890Arg* v);
};
// 0x000D9890
void S_000D9890::fn_000D9890(const S_000D9890Arg* v)
{
    a = v->x;
    b = v->y;
}

struct S_000D5D90
{
    char pad[8];
    unsigned flags;
    char pad2[0x18 - 0xc];
    float v;
    void fn_000D5D90(float x);
};
// 0x000D5D90
void S_000D5D90::fn_000D5D90(float x)
{
    flags &= ~2;
    v = x;
}

struct S_000D5DC0
{
    char pad[8];
    unsigned flags;
    char pad2[0x1c - 0xc];
    float v;
    void fn_000D5DC0(float x);
};
// 0x000D5DC0
void S_000D5DC0::fn_000D5DC0(float x)
{
    flags &= ~2;
    v = x;
}

struct S_000D6640
{
    char pad[0x34];
    float v;
    unsigned flags;
    void fn_000D6640(float x);
};
// 0x000D6640
void S_000D6640::fn_000D6640(float x)
{
    flags |= 0x10000000;
    v = x;
}

struct S_000D9960
{
    char pad[8];
    unsigned flags;
    char pad2[0x50 - 0xc];
    int a;
    char pad3[4];
    unsigned flags2;
    void fn_000D9960(int x);
};
// 0x000D9960
// parked: scheduling
void S_000D9960::fn_000D9960(int x)
{
    flags2 |= 0x10000000;
    a = x;
    flags |= 2;
}

struct S_000D8800
{
    char pad[0x6c];
    int a;
    int b;
    int c;
    void fn_000D8800(int x);
};
// 0x000D8800
void S_000D8800::fn_000D8800(int x)
{
    a = x;
    b = 0;
    c = 0;
}

struct S_000D8820
{
    char pad[0x6c];
    int a;
    int b;
    int c;
    void fn_000D8820(int x);
};
// 0x000D8820
void S_000D8820::fn_000D8820(int x)
{
    a = 0;
    b = x;
    c = 0;
}

struct S_000D8840
{
    char pad[0x6c];
    int a;
    int b;
    int c;
    void fn_000D8840(int x);
};
// 0x000D8840
void S_000D8840::fn_000D8840(int x)
{
    a = 0;
    b = 0;
    c = x;
}
