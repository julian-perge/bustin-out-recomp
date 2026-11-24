struct S_0006DE70_V
{
    virtual ~S_0006DE70_V();
};

struct S_0006DE70
{
    char pad[0x24];
    S_0006DE70_V* p;
    void FUN_0006DE70();
};

// 0x0006DE70
void S_0006DE70::FUN_0006DE70()
{
    if (p) {
        delete p;
        p = 0;
    }
}
