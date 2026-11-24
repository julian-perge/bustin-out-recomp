struct S_001E4040
{
    void FUN_001e4040(int i, short x);
};

// 0x001E4040
void S_001E4040::FUN_001e4040(int i, short x)
{
    ((short*)((char*)this - 0x5e8))[i] = x;
}
