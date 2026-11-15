// 0x00011BB0
const unsigned* fn_00011BB0(const unsigned* a, const unsigned* b)
{
    if (*a < *b)
        a = b;
    return a;
}

// 0x00011BD0
void fn_00011BD0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x00013730
int fn_00013730(char a)
{
    if (a)
        return 0;
    __debugbreak();
    return 1;
}

// 0x00013C40
float fn_00013C40(float t, float a, float b)
{
    return (b - a) * t + a;
}

struct S_0001BB80
{
    char pad0[0x45a1];
    char flag;
    char pad1[0x523c - 0x45a2];
    char out;
    void fn_0001BB80();
};

// 0x0001BB80
void S_0001BB80::fn_0001BB80()
{
    if (!flag)
        out = 1;
}
