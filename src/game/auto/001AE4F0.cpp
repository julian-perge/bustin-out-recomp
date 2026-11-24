struct S_001AE4F0
{
    void FUN_001ae4f0(int i, short x);
};

// 0x001AE4F0
void S_001AE4F0::FUN_001ae4f0(int i, short x)
{
    ((short*)((char*)this - 0x12e))[i] = x;
}
