struct S_000E59C0
{
    char pad[0x148];
    unsigned flags;
    void FUN_000e59c0(int n);
};

// 0x000E59C0
void S_000E59C0::FUN_000e59c0(int n)
{
    flags &= ~(1 << n);
}
