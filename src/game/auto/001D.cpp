struct VB_001D9610
{
    char pad[8];
    int f;
};
struct Base_001D9610
{
    char pad[0x20];
};
struct S_001D9610 : Base_001D9610, virtual VB_001D9610
{
    void FUN_001D9610(int v);
};

// 0x001D9610
void S_001D9610::FUN_001D9610(int v)
{
    f = v;
}

struct S_001D97B0
{
    int pad;
    int x;
    int FUN_001D97B0(const S_001D97B0* o);
};

// 0x001D97B0
int S_001D97B0::FUN_001D97B0(const S_001D97B0* o)
{
    int d = x - o->x;
    return d < 0 ? -d : d;
}
