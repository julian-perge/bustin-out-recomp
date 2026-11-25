struct S_000180F0_obj
{
    virtual ~S_000180F0_obj();
};

struct S_000180F0
{
    int a;
    S_000180F0_obj* obj;
    void FUN_000180f0(int unused);
};

// 0x000180F0
void S_000180F0::FUN_000180f0(int unused)
{
    if (obj) {
        delete obj;
    }
    obj = 0;
}
