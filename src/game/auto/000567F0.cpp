struct V_000567F0
{
    int x, y;
};

struct S_000567F0
{
    bool f;
    int x, y, z;
    void FUN_000567f0(V_000567F0* v, int w);
};

// 0x000567F0
void S_000567F0::FUN_000567f0(V_000567F0* v, int w)
{
    f = true;
    x = v->x;
    y = v->y;
    z = w;
}
