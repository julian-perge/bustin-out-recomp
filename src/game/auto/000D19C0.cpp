struct V_000D19C0
{
    int x, y, z;
};

struct S_000D19C0
{
    char pad[0x50];
    V_000D19C0 v;
    void FUN_000D19C0(const V_000D19C0* p);
};

// 0x000D19C0
void S_000D19C0::FUN_000D19C0(const V_000D19C0* p)
{
    v = *p;
}
