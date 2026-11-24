struct S_001C9C00_E
{
    int d[25];
};

struct S_001C9C00
{
    S_001C9C00_E* base;
    S_001C9C00_E* FUN_001C9C00(int i);
};

// 0x001C9C00
S_001C9C00_E* S_001C9C00::FUN_001C9C00(int i)
{
    return &base[i];
}
