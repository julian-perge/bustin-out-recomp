struct S_001E78A0
{
    int m[3];
    int FUN_001e78a0(int i, int second);
};

// 0x001E78A0
int S_001E78A0::FUN_001e78a0(int i, int second)
{
    if (!second)
        return m[i];
    return m[2];
}
