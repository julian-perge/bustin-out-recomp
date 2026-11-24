struct B_0021BE50
{
    virtual ~B_0021BE50();
};

struct S_0021BE50
{
    B_0021BE50* p;
    void FUN_0021be50();
};

// 0x0021BE50
void S_0021BE50::FUN_0021be50()
{
    if (p)
        delete p;
    p = 0;
}
