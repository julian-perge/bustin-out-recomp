struct P_000d6620
{
    int a;
    int b;
};

struct S_000d6620
{
    char pad0[12];
    int a;
    int b;
    char pad1[39];
    unsigned char fl;
    void FUN_000d6620(const P_000d6620* p);
};

// 0x000D6620
void S_000d6620::FUN_000d6620(const P_000d6620* p)
{
    a = p->a;
    b = p->b;
    fl |= 0x10;
}
