struct S_000e59a0
{
    char pad[0x148];
    unsigned flags;
    void FUN_000e59a0(int n);
};

// 0x000E59A0
void S_000e59a0::FUN_000e59a0(int n)
{
    flags |= 1u << n;
}
