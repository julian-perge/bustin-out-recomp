// 0x001EFBA0
void FUN_001EFBA0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_001EAA30
{
    int x;
    int y;
    void FUN_001EAA30(const S_001EAA30* o);
};

// 0x001EAA30
void S_001EAA30::FUN_001EAA30(const S_001EAA30* o)
{
    y = o->x;
    x = o->y;
}

struct S_001EAA50
{
    int x;
    int y;
    void FUN_001EAA50(S_001EAA50* o);
};

// 0x001EAA50
void S_001EAA50::FUN_001EAA50(S_001EAA50* o)
{
    o->x = y;
    o->y = x;
}

// 0x001EB0D0
int* FUN_001EB0D0(int* a, int* b)
{
    if (*b < *a)
        return b;
    return a;
}

struct Inner_001EF8E0
{
    short* data;
    short get()
    {
        if (data)
            return data[-2];
        return 0;
    }
};
struct S_001EF8E0
{
    char pad[8];
    Inner_001EF8E0* in;
    short FUN_001EF8E0();
};

// 0x001EF8E0
short S_001EF8E0::FUN_001EF8E0()
{
    return in->get();
}

struct S_001EAB50
{
    char pad[0x70];
    int a;
    int b;
    void FUN_001EAB50(const int* p);
};

// 0x001EAB50
void S_001EAB50::FUN_001EAB50(const int* p)
{
    a = p[0];
    b = p[1];
}

struct S_001E42E0
{
    bool FUN_001E42E0();
};

// 0x001E42E0
// parked: source shape
bool S_001E42E0::FUN_001E42E0()
{
    return (*((unsigned char*)this - 0x554) & 1) == 1;
}

struct S_001E4310
{
    bool FUN_001E4310();
};

// 0x001E4310
// parked: source shape
bool S_001E4310::FUN_001E4310()
{
    return (*((unsigned char*)this - 0x554) & 2) == 2;
}

// 0x001E8280
// parked: unclassified
bool FUN_001E8280(int x)
{
    return x <= 0 && x >= -3;
}
