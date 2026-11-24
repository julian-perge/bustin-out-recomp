struct S_000BA700Sub
{
    virtual void FUN_a();
    virtual void FUN_b();
    virtual void FUN_c(int v);
};
struct S_000BA700
{
    char pad[0x48];
    S_000BA700Sub sub;
};
// 0x000BA700
void fn_000BA700(S_000BA700* o, int v)
{
    o->sub.FUN_c(v);
}
