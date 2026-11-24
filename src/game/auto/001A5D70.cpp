struct Inner_001A5D70
{
    char pad0[8];
    short s8;
    char pad1[0x14 - 0xa];
    short s14;
};

struct S_001A5D70
{
    char pad[0x18];
    Inner_001A5D70* in;
    bool FUN_001a5d70();
};

// 0x001A5D70
bool S_001A5D70::FUN_001a5d70()
{
    Inner_001A5D70* i = in;
    if (i->s14)
        return true;
    return i->s8 != 0;
}
