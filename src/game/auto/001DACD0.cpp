struct S_001DACD0_F
{
    unsigned int flags;
    bool IsSet() const { return (flags >> 1) & 1; }
};

struct S_001DACD0
{
    bool FUN_001dacd0();
};

// 0x001DACD0
// parked: source shape
bool S_001DACD0::FUN_001dacd0()
{
    const char* p = (const char*)this;
    const char* q = *(const char**)(p - 0x5ec);
    return ((const S_001DACD0_F*)(*(const char**)(q + 0x14) + (int)p - 0x508))->IsSet();
}
