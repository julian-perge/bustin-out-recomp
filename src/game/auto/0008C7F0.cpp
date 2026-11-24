struct S_0008C7F0
{
    char pad[0x64];
    unsigned f;
    void FUN_0008c7f0(int b);
};

// 0x0008C7F0
void S_0008C7F0::FUN_0008c7f0(int b)
{
    if (b)
        f |= 0x1;
    else
        f &= ~0x1;
}
