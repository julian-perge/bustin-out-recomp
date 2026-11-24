struct S_001AE520
{
    void FUN_001ae520(int i, short x);
};

// 0x001AE520
void S_001AE520::FUN_001ae520(int i, short x)
{
    ((short*)((char*)this - 0x13e))[i] = x;
}
