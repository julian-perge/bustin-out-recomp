struct V_00052010
{
    int v;
};

struct M_00052010
{
    char pad[4];
    V_00052010* p;
};

struct S_00052010
{
    char pad[0x14];
    M_00052010* m;
};

// 0x00052010
int __stdcall FUN_00052010(S_00052010* s)
{
    V_00052010* p = s->m->p;
    return p ? p->v : 0;
}
