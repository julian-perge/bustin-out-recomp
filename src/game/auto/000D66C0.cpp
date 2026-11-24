struct S_000d66c0
{
    char pad0[8];
    unsigned flags;
    char pad1[0x48];
    float f;
    char pad2[3];
    unsigned char fl;
    void FUN_000d66c0(float v);
};

// 0x000D66C0
// parked: scheduling
void S_000d66c0::FUN_000d66c0(float v)
{
    fl |= 0x10;
    f = v;
    flags |= 2;
}
