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

// VC71 puts the or of flags before the store of f, and only a local reference to flags, which steers the compiler, keeps the original order (F-0117).
// 0x000D66C0
// parked: scheduling
void S_000d66c0::FUN_000d66c0(float v)
{
    fl |= 0x10;
    f = v;
    flags |= 2;
}
