struct S_001A5DB0_B
{
    char pad[0x12];
    short k;
};

struct S_001A5DB0
{
    char pad[0x18];
    S_001A5DB0_B* p;
    bool FUN_001a5db0();
};

// 0x001A5DB0
// parked: unclassified
bool S_001A5DB0::FUN_001a5db0()
{
    return p->k == 2;
}
