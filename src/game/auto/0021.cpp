struct S_00218F30
{
    char pad[0x2a1];
    char flag;
    void fn_00218F30();
};

// 0x00218F30
void S_00218F30::fn_00218F30()
{
    if (flag)
        flag = 0;
}

struct S_00219370
{
    char on;
    char pad[0x27];
    int val;
    bool fn_00219370(int v);
};

// 0x00219370
bool S_00219370::fn_00219370(int v)
{
    if (on)
        val = v;
    return true;
}

struct S_002193B0
{
    char on;
    char pad[0x18];
    char val;
    bool fn_002193B0(char v);
};

// 0x002193B0
bool S_002193B0::fn_002193B0(char v)
{
    if (on)
        val = v;
    return true;
}

struct S_00219780
{
    unsigned* head;
    void fn_00219780(unsigned* p);
};

// 0x00219780
void S_00219780::fn_00219780(unsigned* p)
{
    if (p) {
        *p = (unsigned)head;
        head = p;
    }
}

// 0x00219830
void fn_00219830(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_0021B4A0
{
    char m;
    bool fn_0021B4A0(const S_0021B4A0* o);
};

// 0x0021B4A0
// parked: source shape
bool S_0021B4A0::fn_0021B4A0(const S_0021B4A0* o)
{
    return (m & o->m) != 0;
}
