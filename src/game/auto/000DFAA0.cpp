struct S_000dfaa0
{
    char pad0[8];
    unsigned flags;
    char pad1[0x14];
    int v;
    char pad2[0x37];
    unsigned char fl;
    void FUN_000dfaa0(int p);
};

// 0x000DFAA0
// parked: scheduling
void S_000dfaa0::FUN_000dfaa0(int p)
{
    if (p) {
        fl |= 0x10;
        v = p;
        flags |= 2;
    }
}
