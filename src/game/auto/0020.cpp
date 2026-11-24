// 0x0020D800
void fn_0020D800(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x0020D950
void fn_0020D950(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_0020FD40Inner
{
    short* p;
    short size();
};

short S_0020FD40Inner::size()
{
    if (p)
        return p[-2];
    return 0;
}

struct S_0020FD40
{
    char pad[8];
    S_0020FD40Inner* inner;
    short fn_0020FD40();
};

// 0x0020FD40
short S_0020FD40::fn_0020FD40()
{
    return inner->size();
}
