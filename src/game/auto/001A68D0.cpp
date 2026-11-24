struct S_001A68D0Elem
{
    int d[7];
};

struct S_001A68D0
{
    S_001A68D0Elem *base;
    S_001A68D0Elem *FUN_001a68d0(int i);
};

// 0x001A68D0
S_001A68D0Elem *S_001A68D0::FUN_001a68d0(int i)
{
    return &base[i];
}
