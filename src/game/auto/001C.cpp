// 0x001C29D0
void FUN_001C29D0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_001C2890
{
    unsigned short v;
    unsigned short FUN_001C2890();
};

// 0x001C2890
// parked: source shape
unsigned short S_001C2890::FUN_001C2890()
{
    if (v == 0xFFFF)
        return v;
    return v & 0x7FFF;
}

struct S_001C7820
{
    char pad[4];
    unsigned char b4;
    unsigned char b5;
    int FUN_001C7820();
};

// 0x001C7820
int S_001C7820::FUN_001C7820()
{
    if (b4 & 0x80)
        return b5;
    return 10;
}
