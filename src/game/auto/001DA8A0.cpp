struct S_001DA8A0
{
    float a[0x200];
    void FUN_001da8a0(int n, float v);
};

// The function is reached only through a virtual-base thunk, so the negative index stands in for a class layout that VC71 generates (F-0120).
// 0x001DA8A0
// parked: source shape
void S_001DA8A0::FUN_001da8a0(int n, float v)
{
    a[n - 0x152] = v;
}
