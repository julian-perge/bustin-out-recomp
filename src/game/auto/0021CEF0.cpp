struct B_0021CEF0
{
    char pad0[7];
    unsigned char f7;
    char pad1[3];
    unsigned char fb;
};

struct S_0021CEF0
{
    char pad[8];
    B_0021CEF0* p;
    int c;
    bool FUN_0021cef0();
};

// 0x0021CEF0
bool S_0021CEF0::FUN_0021cef0()
{
    if (c && ((p->fb & 0xf0) == 0 || (p->f7 & 2) == 0))
        return true;
    return false;
}
