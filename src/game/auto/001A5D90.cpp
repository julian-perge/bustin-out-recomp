struct S_001A5D90_inner
{
    char pad[0x14];
    short a;
    short b;
};

struct S_001A5D90
{
    char pad[0x18];
    S_001A5D90_inner* p;
    bool FUN_001a5d90();
};

// 0x001A5D90
bool S_001A5D90::FUN_001a5d90()
{
    return p->a != 0 && p->b != -1;
}
