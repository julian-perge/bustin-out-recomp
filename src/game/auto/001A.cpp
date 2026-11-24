// 0x001A0040
void FUN_001A0040(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_001A4FD0
{
    const char* s;
    int FUN_001A4FD0();
};

// 0x001A4FD0
int S_001A4FD0::FUN_001A4FD0()
{
    const char* p = s;
    const char* e = p + 1;
    char c;
    do
        c = *p++;
    while (c);
    return p - e;
}

struct VB_001A6C10
{
    char pad[4];
    int f;
};
struct Base_001A6C10
{
    char pad[0x20];
};
struct S_001A6C10 : Base_001A6C10, virtual VB_001A6C10
{
    void FUN_001A6C10(int v);
};

// 0x001A6C10
void S_001A6C10::FUN_001A6C10(int v)
{
    f = v;
}

struct S_001A6C60
{
    int x;
    int y;
    void FUN_001A6C60(const S_001A6C60& o);
};

// 0x001A6C60
void S_001A6C60::FUN_001A6C60(const S_001A6C60& o)
{
    y = o.y;
    x = o.x;
}

struct S_001AE820
{
    short FUN_001AE820(int i);
};

// 0x001AE820
short S_001AE820::FUN_001AE820(int i)
{
    return (*(short**)((char*)this - 0x14C))[i];
}
