// 0x000F4EE0
void fn_000F4EE0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x000F4F50
void fn_000F4F50(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct Inner_000F5050
{
    char pad[0x74];
    char set;
    char pad2[3];
    int v;
};

struct S_000F5050
{
    char pad[8];
    Inner_000F5050* inner;
    void fn_000F5050(int x);
};

// 0x000F5050
void S_000F5050::fn_000F5050(int x)
{
    Inner_000F5050* p = inner;
    p->v = x;
    p->set = 1;
}

struct S_000F6E80
{
    char pad[0x10c];
    unsigned flags;
    void fn_000F6E80();
};

// 0x000F6E80
void S_000F6E80::fn_000F6E80()
{
    flags &= 0xFFFFFF2F;
    flags |= 0x20;
}
