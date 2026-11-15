struct S_000A2620
{
    char pad[0x84];
    float v;
    void fn_000A2620(float x);
};

// 0x000A2620
void S_000A2620::fn_000A2620(float x)
{
    v = x;
}

struct Inner_000A27D0
{
    char pad[0x1c];
    int v;
};

struct Mid_000A27D0
{
    char pad[0x18];
    Inner_000A27D0* inner;
};

struct S_000A27D0
{
    char pad[0x7c];
    Mid_000A27D0* mid;
    int fn_000A27D0();
};

// 0x000A27D0
int S_000A27D0::fn_000A27D0()
{
    if (mid)
        return mid->inner->v;
    return 0;
}

struct S_000AF6D0
{
    char pad[0xa8];
    float v;
    void fn_000AF6D0(float x);
};

// 0x000AF6D0
void S_000AF6D0::fn_000AF6D0(float x)
{
    v = x;
}
