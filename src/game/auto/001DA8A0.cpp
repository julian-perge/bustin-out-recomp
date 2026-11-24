struct S_001DA8A0
{
    float a[0x200];
    void FUN_001da8a0(int n, float v);
};

// 0x001DA8A0
void S_001DA8A0::FUN_001da8a0(int n, float v)
{
    a[n - 0x152] = v;
}
