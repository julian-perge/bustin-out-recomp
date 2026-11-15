struct S_000E17A0
{
    char pad[0x84];
    int v;
    int fn_000E17A0(int x);
};

// 0x000E17A0
// parked: source shape
int S_000E17A0::fn_000E17A0(int x)
{
    v = x;
    return x;
}

struct Sub_000EFD90
{
    virtual void v0();
    virtual void v1();
};

struct Mid_000EFD90
{
    char pad[0x84];
    Sub_000EFD90* sub;
};

struct S_000EFD90
{
    char pad[8];
    Mid_000EFD90* mid;
    void fn_000EFD90(int a);
};

// 0x000EFD90
void S_000EFD90::fn_000EFD90(int a)
{
    mid->sub->v1();
}
