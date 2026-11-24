struct V_000577D0
{
    int v;
};

struct M_000577D0
{
    char pad[8];
    V_000577D0* p;
};

struct S_000577D0
{
    char pad[0x14];
    M_000577D0* m;
};

// 0x000577D0
int __stdcall FUN_000577d0(S_000577D0* s)
{
    V_000577D0* p = s->m->p;
    return p ? p->v : 0;
}
