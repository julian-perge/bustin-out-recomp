struct S_0008C810
{
    char pad[0x64];
    unsigned f;
    void FUN_0008c810(int b);
};

// 0x0008C810
void S_0008C810::FUN_0008c810(int b)
{
    if (b)
        f |= 0x8;
    else
        f &= ~0x8;
}
