struct S_001B66A0
{
    void FUN_001b66a0(int* out);
};

// The function is reached only through a virtual-base thunk, so the cast stands in for a class layout that VC71 generates (F-0120).
// 0x001B66A0
// parked: source shape
void S_001B66A0::FUN_001b66a0(int* out)
{
    const int* p = (const int*)this;
    out[0] = p[-33];
    out[1] = p[-32];
}
