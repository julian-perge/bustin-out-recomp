struct S_001E83F0
{
    char pad[0x588];
    int a;
    char b;
    bool FUN_001e83f0();
};

// 0x001E83F0
bool S_001E83F0::FUN_001e83f0()
{
    if (b)
        return false;
    return a != 0;
}
