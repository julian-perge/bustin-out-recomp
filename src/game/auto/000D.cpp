// 0x000D6570
void fn_000D6570(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct Inner_000D9820
{
    char pad[0xc];
    float v;
};

struct S_000D9820
{
    char pad[0x44];
    Inner_000D9820* inner;
    void fn_000D9820(float x);
};

// 0x000D9820
void S_000D9820::fn_000D9820(float x)
{
    inner->v = x;
}

// 0x000DF880
void fn_000DF880(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}
