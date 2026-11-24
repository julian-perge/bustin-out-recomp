struct S_0008C830
{
    char pad[0x64];
    unsigned f;
    void FUN_0008c830(int b);
};

// 0x0008C830
void S_0008C830::FUN_0008c830(int b)
{
    if (b)
        f |= 0x4;
    else
        f &= ~0x4;
}
