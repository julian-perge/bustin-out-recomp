struct P_000E62A0
{
    char pad[0x50];
    bool f;
};

struct S_000E62A0
{
    char pad[0xe8];
    P_000E62A0* p;
    bool FUN_000e62a0();
};

// 0x000E62A0
bool S_000E62A0::FUN_000e62a0()
{
    return p && p->f;
}
