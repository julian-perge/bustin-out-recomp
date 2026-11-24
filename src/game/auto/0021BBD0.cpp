struct B_0021BBD0
{
    virtual ~B_0021BBD0();
};

struct S_0021BBD0
{
    B_0021BBD0* p;
    void FUN_0021bbd0();
};

// 0x0021BBD0
void S_0021BBD0::FUN_0021bbd0()
{
    if (p)
        delete p;
    p = 0;
}
